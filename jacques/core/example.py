from __future__ import annotations
import ast
import re
from typing import TYPE_CHECKING
import numpy as np
import pandas as pd
from jacques.ast.jacques_ast_utils import (
    SubtreeBuilder,
    extract_subtree_by_ref_as_ref_list,
)
from jacques.core.jacques_member import JacquesMember
from jacques.core.rule import ConditionalRule, Rule
from jacques.utils import is_superstring
from jacques.world_knowledge import *


if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from jacques.ast.jacques_ast import CodeJAST, DslJAST


class Example(JacquesMember):
    def __init__(self, jacques, dsl_source: str, code_source: str) -> None:
        self.dsl_source = dsl_source
        self.code_source = code_source
        super().__init__(jacques)

    def __str__(self) -> str:
        return f"{self.__class__}\n\t{self.dsl_source}\n\t{self.code_source}"

    def _deconstruct_dsl_source(self) -> List[str]:
        return self.dsl_source.split(" | ")

    def matrix(self) -> _ExampleMatrix:
        dsl_jast_list = list(self.jacques.dsl_parser.parse(self.dsl_source))
        code_jast_list = list(self.jacques.python_parser.parse(self.code_source))
        return _ExampleMatrix(self.jacques, dsl_jast_list, code_jast_list)

    @property
    def is_exhausted(self) -> bool:
        m = self.matrix()
        return m.exhausted

    def matches(self) -> List[Tuple[DslJAST, CodeJAST, List[CodeJAST]]]:
        return self.matrix().matches()


class _ExampleMatrix:
    def __init__(
        self,
        jacques,
        dsl_header: List[DslJAST],
        code_header: List[CodeJAST],
    ) -> None:
        self.jacques = jacques
        self.dsl_header = dsl_header
        self.code_header = code_header
        self.y = len(dsl_header)
        self.x = len(code_header)
        self.m = np.zeros((self.y, self.x), dtype=int)
        self.pipe_nodes = [[] for i in range(self.y)]

        root_partitions = self._root_partitions(code_header[0], self.y - 1)
        for root_partition in root_partitions:
            self._write_partition_into_matrix(root_partition)
        self._load_hypothetical_pipe_nodes()
        self._update_with_rules()

    def _load_hypothetical_pipe_nodes(self):
        for i in range(1, self.y):
            pipe_node_hypothesis = [
                self.code_header[x] for x in list(np.where(self.m[i] == 1)[0])
            ]
            self.pipe_nodes[i - 1].extend(pipe_node_hypothesis)

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
        self, code_jast: CodeJAST, dsl_inverse_depth
    ) -> List[List[CodeJAST]]:
        subparts = []
        for child in code_jast.children:
            subparts.extend(self._root_partitions_rec(child, dsl_inverse_depth - 1))
        return [[code_jast] + subpart for subpart in subparts]

    def _root_partitions_rec(
        self, code_jast: CodeJAST, dsl_inverse_depth
    ) -> List[List[CodeJAST]]:
        if dsl_inverse_depth == 0:
            return [[code_jast]]
        elif dsl_inverse_depth > code_jast.inverse_depth:
            return []
        else:
            subparts = []
            subparts_skipping = []
            for child in code_jast.children:
                subparts.extend(self._root_partitions_rec(child, dsl_inverse_depth - 1))
                if code_jast.inverse_depth > dsl_inverse_depth:
                    subparts_skipping.extend(
                        self._root_partitions_rec(child, dsl_inverse_depth)
                    )
            subparts = [[code_jast] + subpart for subpart in subparts]
            return subparts + subparts_skipping

    def _update_with_rules(self) -> None:
        for rule in self.jacques.ruleset.values():
            self._update_with_rule(rule)

    def _update_with_rule(self, rule: Rule) -> None:
        for i, dsl_jast in reversed(list(enumerate(self.dsl_header))):
            # TODO: resolve pipe nodes
            if re.match(rule.regex_dsl, dsl_jast.dsl_string):
                # We exclude nodes that could not match the dsl right away:
                m = ~self.m[i, :].astype(bool)
                code_header_legal_subset = list(
                    np.ma.array(self.code_header, mask=m).compressed()
                )

                generated_code = self.jacques.code_generator(
                    EVAL_PIPE_PREFIX + " " + dsl_jast.dsl_string
                )
                if len(generated_code) != 1:
                    continue
                generated_code = generated_code[0]
                # Now we check every legal node for the match:
                for code_jast in code_header_legal_subset:
                    if isinstance(rule, ConditionalRule):
                        for rule_code_jast in rule.code_jasts.values():
                            matched_code_jast_list = extract_subtree_by_ref_as_ref_list(
                                code_jast, rule_code_jast
                            )
                            if matched_code_jast_list and is_superstring(
                                code_jast.source_code, generated_code
                            ):
                                self.m[i, :] = 0
                                for code_jast in matched_code_jast_list:
                                    self.m[:, self.code_header.index(code_jast)] = 0
                                self.pipe_nodes[i - 1] = [matched_code_jast_list[0]]
                    elif isinstance(rule, Rule):
                        matched_code_jast_list = extract_subtree_by_ref_as_ref_list(
                            code_jast, rule.code_jast
                        )
                        if matched_code_jast_list and is_superstring(
                            code_jast.source_code, generated_code
                        ):
                            self.m[i, :] = 0
                            for code_jast in matched_code_jast_list:
                                self.m[:, self.code_header.index(code_jast)] = 0
                            self.pipe_nodes[i - 1] = [matched_code_jast_list[0]]

    @property
    def exhausted(self):
        return self.m.sum() == 0

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
        return matches

    def matches(self) -> List[Tuple[DslJAST, CodeJAST, List[CodeJAST]]]:
        matches = self._compute_matches()
        result = []
        for i, js in reversed(matches.items()):
            dsl_jast = self.dsl_header[i]
            code_jasts = [self.code_header[j] for j in js]
            codejast_complete_subtree = SubtreeBuilder().build(code_jasts)

            result.append((dsl_jast, codejast_complete_subtree, self.pipe_nodes[i]))
        return result
