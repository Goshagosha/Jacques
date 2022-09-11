from __future__ import annotations
import ast
import re
from typing import TYPE_CHECKING
import numpy as np
import pandas as pd
from jacques.ast.jacques_ast_utils import (
    CodeExtractor,
    SubtreeBuilder,
    extract_subtree_by_reference_as_reference_list,
)
from jacques.core.jacques_member import JacquesMember
from jacques.core.rule import Rule


if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from jacques.ast.jacques_ast import CodeJAST, DslJAST


class Example(JacquesMember):
    def __init__(self, jacques, dsl_source: str, code_source: str) -> None:
        self.dsl_source = dsl_source
        self.code_source = code_source
        super().__init__(jacques)

    def _deconstruct_dsl_source(self) -> List[str]:
        return self.dsl_source.split(" | ")

    def matrix(self) -> _ExampleMatrix:
        dsl_jast = self.jacques.dsl_parser.parse(self.dsl_source)
        code_jast = self.jacques.python_parser.parse(self.code_source)
        return _ExampleMatrix(self.jacques, list(dsl_jast), list(code_jast))

    @property
    def is_exhausted(self) -> bool:
        return self.matrix().exhausted

    def matches(self) -> List[Tuple[DslJAST, CodeJAST]]:
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

        y = len(dsl_header)
        x = len(code_header)
        self.m = np.zeros((y, x), dtype=int)
        for i in range(y):
            for j in range(x):
                if (
                    i <= code_header[j].depth
                    and code_header[j].inverse_depth + i >= y - 1
                ):
                    self.m[i, j] = 1
        self._update_with_rules()

    def _update_with_rules(self) -> None:
        for rule in self.jacques.ruleset.values():
            self._update_with_rule(rule)

    def _update_with_rule(self, rule: Rule) -> None:
        for i, dsl_jast in reversed(list(enumerate(self.dsl_header))):
            if re.match(rule.regex_dsl, dsl_jast.dsl_string):
                m = ~self.m[i, :].astype(bool)
                code_header_legal_subset = list(
                    np.ma.array(self.code_header, mask=m).compressed()
                )
                for code_jast in code_header_legal_subset:
                    matched_code_jast_list = (
                        extract_subtree_by_reference_as_reference_list(
                            code_jast, rule.code_jast
                        )
                    )
                    if matched_code_jast_list:
                        break
                if matched_code_jast_list:
                    self.m[i, :] = 0

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

    def _compute_matches(self) -> Dict[int, List[int]]:
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

    def matches(self) -> List[Tuple[DslJAST, CodeJAST]]:
        matches = self._compute_matches()
        result = []
        for i, js in matches.items():
            dsl_jast = self.dsl_header[i]
            code_jasts = [self.code_header[j] for j in js]
            codejast_complete_subtree = SubtreeBuilder().build(code_jasts)

            result.append((dsl_jast, codejast_complete_subtree))
        return result
