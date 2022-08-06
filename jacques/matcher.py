from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from jacques.rule import Rule
    from typing import Dict, List, Tuple
    from jacques.j_ast import CodeJAST, DslJAST


class ExampleMatrix:
    def __init__(
        self,
        dsl_header: List[Tuple[str, DslJAST]],
        code_header: List[Tuple[str, CodeJAST]],
    ) -> None:
        self.dsl_header = dsl_header
        self.code_header = code_header

        y = len(dsl_header)
        x = len(code_header)
        self.m = np.zeros((y, x), dtype=int)
        for i in range(y):
            for j in range(x):
                if (
                    i <= code_header[j][1].depth
                    and code_header[j][1].inverse_depth + i >= y - 1
                ):
                    self.m[i, j] = 1

    def update_with_rules(self, ruleset: Dict[str, Rule]) -> None:
        for (rule_dsl_name, rule) in ruleset.items():
            indices = [
                i
                for i, (name, _) in enumerate(self.dsl_header)
                if rule_dsl_name == name
            ]
            self.m[indices, :] = 0
            raise NotImplementedError
            # TODO
            # Proper rule handling

    def exhausted(self):
        return self.m.sum() == 0

    def __str__(self) -> str:
        return str(
            pd.DataFrame(
                self.m,
                index=[name for name, _ in self.dsl_header],
                columns=[name for name, _ in self.code_header],
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
            continue
        return matches

    def matches(self) -> List[Tuple[DslJAST, List[CodeJAST]]]:
        matches = self.__find_matches()
        result = []
        for i, js in matches.items():
            dsl_jast = self.dsl_header[i][1]
            code_jasts = [self.code_header[j][1] for j in js]
            result.append((dsl_jast, code_jasts))
        return result


class Matcher:
    def __init__(self, jacques):
        self.jacques = jacques
        self.examples = []

    def push_example(self, dsl_jast: DslJAST, code_jast: CodeJAST) -> None:
        dsl_header = dsl_jast.named_deconstructed()
        code_header = code_jast.named_deconstructed()

        m = ExampleMatrix(dsl_header, code_header)
        self.examples.append(m)

    def _update_with_rules_and_dump_exhausted(self) -> bool:
        dumped = False
        for example_matrix in self.examples:
            example_matrix.update_with_rules(self.jacques.ruleset)
        updated_examples = []
        for example_matrix in self.examples:
            if example_matrix.exhausted():
                dumped = True
            else:
                updated_examples.append(example_matrix)
        self.examples = updated_examples
        return dumped
