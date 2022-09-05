from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
import pandas as pd
from jacques.core.jacques_member import JacquesMember
from ..ast.jacques_ast_utils import extract_subtree_by_reference_as_reference_list


if TYPE_CHECKING:
    from jacques.core.rule import Rule
    from typing import Dict, List, Tuple
    from jacques.ast.jacques_ast import CodeJAST, DslJAST


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

    def apply_rule(self, rule: Rule) -> None:
        row = np.where(
            np.array([d.command for d in self.dsl_header])
            == rule.original_dsl_jast.command
        )[0]
        possible_code_jast_names = [c.command for c in rule.original_code_jast]
        for i, command in enumerate([c.command for c in self.code_header]):
            if command not in possible_code_jast_names:
                self.m[row, i] = 0

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


class Matcher(JacquesMember):
    def __init__(self, jacques):
        self.examples = []
        super().__init__(jacques)

    def push_example(self, dsl_jast: DslJAST, code_jast: CodeJAST) -> None:
        dsl_header = list(dsl_jast)
        code_header = list(code_jast)

        m = ExampleMatrix(dsl_header, code_header)
        self.examples.append(m)

    def _update_with_rules_and_dump_exhausted(self) -> bool:
        dumped = False
        for example_matrix in self.examples:
            for rule in self.jacques.ruleset.values():
                example_matrix.apply_rule(rule)
        updated_examples = []
        for example_matrix in self.examples:
            if example_matrix.exhausted():
                dumped = True
            else:
                updated_examples.append(example_matrix)
        self.examples = updated_examples
        return dumped
