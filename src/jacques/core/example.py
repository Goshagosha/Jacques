"""This module contains most if not all complex tree matching logic algorithms.
Lasciate ogni speranza, voi ch'entrate."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from uuid import uuid4 as uuid
from loguru import logger
import numpy as np
import pandas as pd
from ..ast.jacques_ast_utils import (
    SubtreeBuilder,
    extract_subtree_by_ref_as_ref_list,
)
from ..ast.python_ast_cross_comparer import Comparer
from .jacques_member import JacquesMember
from .rule import ConditionalRule, Rule

# Prevent pandas from truncating the output and making linebreaks
pd.set_option("display.max_columns", None)
pd.options.display.width = 0

if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from src.jacques.ast.jacques_ast import CodeJAST, DslJAST


class Example(JacquesMember):
    def __init__(self, jacques, dsl_source: str, code_source: str) -> None:
        self.dsl_source = dsl_source
        self.code_source = code_source
        self.id = uuid().hex
        super().__init__(jacques)

    def __str__(self) -> str:
        return f"{self.__class__}\n\t{self.dsl_source}\n\t{self.code_source}"

    def _deconstruct_dsl_source(self) -> List[str]:
        return self.dsl_source.split(" | ")

    def matrix(self) -> _ExampleMatrix:
        dsl_jast_list = list(self.jacques.dsl_parser.parse(self.dsl_source))
        code_jast_list = list(
            self.jacques.python_parser.parse(self.code_source)
        )
        return _ExampleMatrix(
            self.jacques, self.id, dsl_jast_list, code_jast_list
        )

    @property
    def is_exhausted(self) -> bool:
        m = self.matrix()
        return m.exhausted

    def matches(self) -> List[Tuple[DslJAST, CodeJAST, List[CodeJAST]]]:
        return self.matrix().matches()


class _ExampleMatrix:  # pylint: disable=too-many-instance-attributes # science is complex
    def __init__(
        self,
        jacques,
        example_id: str,
        dsl_header: List[DslJAST],
        code_header: List[CodeJAST],
    ) -> None:
        self.jacques = jacques
        self.dsl_header = dsl_header
        self.code_header = code_header
        self.y = len(dsl_header)
        self.x = len(code_header)
        self.m = np.zeros((self.y, self.x), dtype=int)
        self.pipe_nodes = [[] for _ in range(self.y)]
        self.example_id = example_id

        root_partitions = self._root_partitions(code_header[0], self.y - 1)
        for root_partition in root_partitions:
            self._write_partition_into_matrix(root_partition)
        self._update_with_rules()
        self._update_with_exceptions()
        logger.debug(f"Example matrix:\n{self}")
        with logger.contextualize(latex=True):
            logger.debug(self.to_latex_table())
        if self.jacques.cross_compare_on:
            self._cross_compares()
            logger.debug(f"Example matrix after cross_compare:\n{self}")

    def _cross_compares(  # pylint: disable=too-many-branches # science is complex
        self,
    ) -> None:
        cross_compare_matrix = np.zeros((self.y, self.x), dtype=int)
        for i in range(self.x):
            cross_compare_column = [0] * self.y
            code_jast = self.code_header[i]
            for j in range(self.y):
                dsl_jast = self.dsl_header[j]
                for arg in dsl_jast.deconstructed:
                    try:
                        matches = Comparer(arg).compare(code_jast.code_ast)
                    except AttributeError as e:
                        logger.debug(f"Error in cross_compare: {e}")
                        matches = 0
                    cross_compare_column[j] += matches
            cross_compare_matrix[:, i] = cross_compare_column
        logger.debug(f"Crosscompare matrix compared:\n{cross_compare_matrix}")
        for i in range(self.x):
            code_jast = self.code_header[i]
            for child in code_jast.children:
                k = self.code_header.index(child)
                cross_compare_matrix[:, i] -= cross_compare_matrix[:, k]
        logger.debug(f"Crosscompare folded:\n{cross_compare_matrix}")
        for i in range(self.x):
            if max(cross_compare_matrix[:, i]) == 0:
                continue
            cross_compare_matrix[:, i] = [
                1
                if cross_compare_matrix[j, i] == max(cross_compare_matrix[:, i])
                else 0
                for j in range(self.y)
            ]
        logger.debug(f"Crosscompare regularized:\n{cross_compare_matrix}")
        for i in range(self.y):
            for j in range(self.x):
                if self.m[i, j] == 0:
                    cross_compare_matrix[i, j] = 0
        for i in range(self.y):
            if max(cross_compare_matrix[:, i]) == 0:
                cross_compare_matrix[:, i] = self.m[:, i]
        self.m = cross_compare_matrix

    def _write_partition_into_matrix(self, root_partition: List[CodeJAST]):
        def write_children(code_jast: CodeJAST, i: int):
            for child in code_jast.children:
                if child not in root_partition:
                    self.m[i, self.code_header.index(child)] = 1
                    write_children(child, i)

        for i, code_jast in enumerate(root_partition):
            self.m[i, self.code_header.index(code_jast)] = 1
            write_children(code_jast, i)

    def _root_partitions(
        self, code_jast: CodeJAST, dsl_height
    ) -> List[List[CodeJAST]]:
        subparts = []
        for child in code_jast.children:
            subparts.extend(self._root_partitions_rec(child, dsl_height - 1))
        if subparts:
            return [[code_jast] + subpart for subpart in subparts]
        return [[code_jast]]

    def _root_partitions_rec(
        self, code_jast: CodeJAST, dsl_height
    ) -> List[List[CodeJAST]]:
        if dsl_height == 0:
            subparts = [[code_jast]]
            for child in code_jast.children:
                subparts.extend(self._root_partitions_rec(child, dsl_height))
            return subparts
        if dsl_height > code_jast.height:
            return []
        subparts = []
        subparts_skipping = []
        for child in code_jast.children:
            subparts.extend(self._root_partitions_rec(child, dsl_height - 1))
            if code_jast.height > dsl_height:
                subparts_skipping.extend(
                    self._root_partitions_rec(child, dsl_height)
                )
        subparts = [[code_jast] + subpart for subpart in subparts]
        return subparts + subparts_skipping

    def _update_with_rules(self) -> None:
        for rule in self.jacques.ruleset.values():
            self._update_with_rule(rule)

    def _update_with_exceptions(self) -> None:
        if self.example_id in self.jacques.except_matches:
            for exception_regex in self.jacques.except_matches[self.example_id]:
                for i, code_jast in enumerate(self.code_header):
                    if re.match(exception_regex, code_jast.source_code):
                        self.m[:, i] = 0

    def _update_with_rule(  # pylint: disable=too-many-branches # science
        self, rule: Rule
    ) -> None:
        for i, dsl_jast in reversed(  # pylint: disable=too-many-nested-blocks
            list(enumerate(self.dsl_header))
        ):
            dsl_regex_match = re.match(rule.regex_dsl, dsl_jast.dsl_string)
            if dsl_regex_match:
                # We exclude nodes that could not match the dsl right away:
                m = ~self.m[i, :].astype(bool)
                code_header_legal_subset = list(
                    np.ma.array(self.code_header, mask=m).compressed()
                )

                # Now we check every legal node for the match:
                for code_jast in code_header_legal_subset:
                    if isinstance(rule, ConditionalRule):
                        for rule_code_jast in rule.code_jasts.values():
                            code_regex_match = re.match(
                                rule.regex_code, code_jast.source_code
                            )
                            if code_regex_match:
                                not_matched = False
                                for k, v in dsl_regex_match.groupdict().items():
                                    if k not in code_regex_match.groupdict():
                                        not_matched = True
                                        break
                                    if v not in code_regex_match.group(k):
                                        not_matched = True
                                        break
                                if not_matched:
                                    continue
                                matched_code_jast_list = (
                                    extract_subtree_by_ref_as_ref_list(
                                        code_jast, rule_code_jast
                                    )
                                )
                                if matched_code_jast_list:
                                    self.m[i, :] = 0
                                    for code_jast in matched_code_jast_list:
                                        self.m[
                                            :, self.code_header.index(code_jast)
                                        ] = 0
                                    self.pipe_nodes[i - 1].append(
                                        matched_code_jast_list[0]
                                    )
                    elif isinstance(rule, Rule):
                        code_regex_match = re.match(
                            rule.regex_code, code_jast.source_code
                        )
                        if code_regex_match:
                            not_matched = False
                            for k, v in dsl_regex_match.groupdict().items():
                                if k not in code_regex_match.groupdict():
                                    not_matched = True
                                    break
                                if v not in code_regex_match.group(k):
                                    not_matched = True
                                    break
                            if not_matched:
                                continue
                            matched_code_jast_list = (
                                extract_subtree_by_ref_as_ref_list(
                                    code_jast, rule.code_jast
                                )
                            )
                            if matched_code_jast_list:
                                self.m[i, :] = 0
                                for code_jast in matched_code_jast_list:
                                    self.m[
                                        :, self.code_header.index(code_jast)
                                    ] = 0
                                self.pipe_nodes[i - 1].append(
                                    matched_code_jast_list[0]
                                )

    @property
    def exhausted(self):
        return self.m.sum() == 0

    def to_latex_table(self):
        # pylint: disable=anomalous-backslash-in-string # latex things
        result = "\\begin{blockarray}{" + "c" * (self.x + 1) + "}\n"
        for x in range(self.x):
            result += "& \\text{\pw{" + self.code_header[x].command + "}}"
        result += "\\\\\n"
        result += "\\begin{block}{c[" + self.x * "c" + "]}\n"
        for y in range(self.y):
            result += "\\text{\pw{" + self.dsl_header[y].command + "}}"
            for x in range(self.x):
                result += " & " + str(int(self.m[y, x]))
            result += " \\\\\n"
        result += "\\end{block}\n"
        result += "\\end{blockarray}\n"
        return f"\n\[\n{result}\]"

    def __str__(self) -> str:
        return str(
            pd.DataFrame(
                self.m,
                index=[d.command for d in self.dsl_header],
                columns=[code.command for code in self.code_header],
            )
        )

    def __repr__(self) -> str:
        return str(self)

    def _compute_matches(self) -> Dict[int, Tuple[List[int]]]:
        matches = {}
        y, x = self.m.shape
        for i in range(y):
            solved = False
            for j in range(x):
                # if we find a TRUE cell, we check whole column
                if self.m[i, j]:
                    solved = True
                    # if this row(dsl) for this column(code) is not unique - skip to next row(dsl)
                    if self.m[:, j].sum() != 1:
                        solved = False
                        break
            if solved:
                matches[i] = list(np.where(self.m[i] == 1)[0])
                if i > 0:
                    self.pipe_nodes[i - 1].append(
                        self.code_header[matches[i][0]]
                    )
        return matches

    def matches(self) -> List[Tuple[DslJAST, CodeJAST, List[CodeJAST]]]:
        matches = self._compute_matches()
        result = []
        for i, js in reversed(matches.items()):  # pylint: disable=invalid-name
            dsl_jast = self.dsl_header[i]
            code_jasts = [self.code_header[j] for j in js]
            codejast_complete_subtree = SubtreeBuilder().build(code_jasts)
            if not self.pipe_nodes[i] and i < self.y - 1:
                self.pipe_nodes[i] = [
                    self.code_header[k]
                    for k in list(np.where(self.m[i + 1] == 1)[0])
                ]
            result.append(
                (dsl_jast, codejast_complete_subtree, self.pipe_nodes[i])
            )
        return result
