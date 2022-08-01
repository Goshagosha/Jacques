import numpy as np
import pandas as pd

from jacques.j_ast import DslJAST


class ExampleMatrix(pd.DataFrame):
    def __init__(self, dsl_header, code_header) -> None:
        i = len(dsl_header)
        j = len(code_header)
        data = np.zeros((i, j))
        k = i - 1
        super().__init__(data, index=dsl_header.keys(), columns=code_header.keys())
        for (i, jast) in enumerate(dsl_header.values()):
            print(jast.command)
            if i - k < 1:
                self.iloc[i][i] = 1
            self.iloc[i][i : i - k] = 1


class Matcher:
    def __init__(self, jacques):
        self.world_knowledge = jacques.world_knowledge
        self.problem_knowledge = jacques.problem_knowledge

    def load_sample(self, dsl_jast, code_jast) -> None:
        dsl_header = {}
        code_header = {}
        current = dsl_jast
        while len(current.children) > 0:
            dsl_header[current.command] = current
            current = current.children[0]

        code_jast_queue = [code_jast]
        while True:
            current = code_jast_queue[0]
            code_header[current.command] = current
            code_jast_queue.extend(current.children)
            if len(code_jast_queue) == 1:
                break
            code_jast_queue = code_jast_queue[1:]

        m = ExampleMatrix(dsl_header, code_header)
        print(m)
