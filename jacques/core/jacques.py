from __future__ import annotations
from typing import Dict, List, Tuple
from jacques.ast.jacques_ast import CodeJAST, DslJAST
from jacques.core.nldsl_utils import generate_function
from jacques.parsers.dsl_parser import DslParser
from jacques.parsers.python_parser import PythonParser
from jacques.core.rule import Rule
from jacques.core.rule_synthesizer import RuleSynthesizer
from jacques.core.example import Example, _ExampleMatrix
from nldsl import CodeGenerator


class Jacques:
    def __init__(self, world_knowledge) -> None:
        self.world_knowledge = world_knowledge
        self.encountered_objects: List[str] = []

        self.code_generator = CodeGenerator()
        self.examples = []
        self.dsl_parser = DslParser(jacques=self)
        self.python_parser = PythonParser(jacques=self)
        self._rule_synthesizer = RuleSynthesizer(jacques=self)
        self.ruleset: Dict[str, Rule] = {}

    def _generate_rules(self, matches) -> None:
        rules = self._rule_synthesizer.from_matches(matches)
        self.ruleset.update(rules)

    def _update_codegen(self) -> None:
        rule: Rule
        for name, rule in self.ruleset.items():
            function = generate_function(rule)
            self.code_generator.register_function(function, name)

    def process_all_examples(self):
        finished = False
        while not finished:
            finished = True
            example: Example
            for example in self.examples:
                # for rule in self.ruleset.values():
                #     example.apply_rule(rule)
                matches = example.matches()
                self._generate_rules(matches)
                self._update_codegen()
                anything_else_dumped = False  # Check if any matrices were updated
                finished = finished and not anything_else_dumped

    def push_example(self, dsl_string: str, code_string: str) -> None:
        if dsl_string.startswith("## "):
            dsl_string = dsl_string[3:]
        self.examples.append(Example(self, dsl_string, code_string))

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
