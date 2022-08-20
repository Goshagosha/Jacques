from __future__ import annotations
from typing import Dict, List, Tuple
from jacques.jast import CodeJAST, DslJAST
from jacques.matcher import ExampleMatrix, Matcher
from jacques.parser.dsl_parser import DslParser
from jacques.parser.python_parser import PythonParser
from jacques.rule import Rule, RuleSynthesizer

import jacques.world_knowledge as world_knowledge


class JastStorage:
    def __init__(self) -> None:
        self.code_jasts: List[CodeJAST] = []
        self.dsl_jasts: List[List[DslJAST]] = []

    def push(self, dsl_jast: DslJAST, code_jast: CodeJAST) -> None:
        self.code_jasts.append(code_jast)
        self.dsl_jasts.append(list(dsl_jast))

    def get_samples(self, dsl_command_name: str) -> List[Tuple[DslJAST, CodeJAST]]:
        samples = []
        for i, dsl_jast_list in enumerate(self.dsl_jasts):
            for dsl_jast in dsl_jast_list:
                if dsl_jast.command == dsl_command_name:
                    samples.append((dsl_jast, self.code_jasts[i]))
        return samples


class Jacques:
    def __init__(self, world_knowledge) -> None:
        self.world_knowledge = world_knowledge
        self.encountered_objects: List[str] = []

        self.dsl_parser = DslParser(jacques=self)
        self.python_parser = PythonParser(jacques=self)
        self.matcher = Matcher(jacques=self)
        self.rule_synthesizer = RuleSynthesizer(jacques=self)
        self.ruleset: Dict[str, Rule] = {}
        self.jast_storage: JastStorage = JastStorage()

    def append_rules(self, new_rules) -> None:
        self.ruleset.extend(new_rules)
        self.ruleset = list(set(self.ruleset))

    def _rules_from_matches(self, matches) -> None:
        rules = self.rule_synthesizer.from_matches(matches)
        self.ruleset.update(rules)

    def process_all_examples(self):
        finished = False
        while not finished:
            finished = True
            example_matrix: ExampleMatrix
            for example_matrix in self.matcher.examples:
                matches = example_matrix.matches()
                self._rules_from_matches(matches)
                anything_else_dumped = (
                    self.matcher._update_with_rules_and_dump_exhausted()
                )
                finished = finished and not anything_else_dumped

    def push_example(self, dsl_string, code_string) -> None:
        dsl_tree = self.dsl_parser.parse(dsl_string)
        code_tree = self.python_parser.parse(code_string)
        self.jast_storage.push(dsl_tree, code_tree)
        self.matcher.push_example(dsl_tree, code_tree)

    def push_examples_from_file(self, path: str) -> None:
        dsl = None
        with open(path, "r") as file:
            next_line_is_code = False
            for line in file.readlines():
                if next_line_is_code:
                    self.push_example(dsl, line)
                    next_line_is_code = False
                    dsl = None
                elif line.startswith("##"):
                    dsl = line[3:]
                    next_line_is_code = True


j = Jacques(world_knowledge)

py = "data = pd.DataFrame(other_df, columns=['Country/Region', 'Confirmed']).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min confirmed'}).sort_values(['Min confirmed'], axis='index', ascending=[False]).info(verbose=False)"
j.encountered_objects = ["data", "df1"]
cj = j.python_parser.parse(py)


j.push_examples_from_file("./test.py")
j.process_all_examples()
