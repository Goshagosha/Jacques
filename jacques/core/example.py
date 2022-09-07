from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
import pandas as pd
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

    def apply_rule(self, rule: Rule) -> None:
        self.dsl_source = rule.scrap_dsl(self.dsl_source)
        self.code_source = rule.scrap_code(self.code_source)

    def to_matrix(self) -> ExampleMatrix:
        dsl_jast = self.jacques.dsl_parser.parse(self.dsl_source)
        code_jast = self.jacques.python_parser.parse(self.code_source)
        return ExampleMatrix(list(dsl_jast), list(code_jast))


class ExampleMatrix:
    def __init__(
        self,
        dsl_header: List[DslJAST],
        code_header: List[CodeJAST],
    ) -> None:
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

    def __find_matches(self) -> Dict[int, List[int]]:
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

    def matches(self) -> List[Tuple[DslJAST, List[CodeJAST]]]:
        matches = self.__find_matches()
        result = []
        for i, js in matches.items():
            dsl_jast = self.dsl_header[i]
            code_jasts = [self.code_header[j] for j in js]
            result.append((dsl_jast, code_jasts))
        return result
