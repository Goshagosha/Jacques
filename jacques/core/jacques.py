from __future__ import annotations
from typing import Dict, List, Tuple
from jacques.ast.jacques_ast import CodeJAST, DslJAST
from jacques.parsers.dsl_parser import DslParser
from jacques.parsers.python_parser import PythonParser
from jacques.core.rule import Rule
from jacques.core.rule_synthesizer import RuleSynthesizer
from jacques.core.example import Example, ExampleMatrix
from nldsl import CodeGenerator, grammar


class JastStorage:
    """NEVER USED"""

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

        self.code_generator = CodeGenerator()
        self.examples = []
        self.dsl_parser = DslParser(jacques=self)
        self.python_parser = PythonParser(jacques=self)
        self.rule_synthesizer = RuleSynthesizer(jacques=self)
        self.ruleset: Dict[str, Rule] = {}
        self.context = {"grammar": grammar}

    def _rules_from_matches(self, matches) -> None:
        rules = self.rule_synthesizer.from_matches(matches)
        for name, rule in rules.items():
            dsl_grammar = rule.original_dsl_jast.reconstruct_to_nldsl()
            f = rule.generate_function(name, dsl_grammar)
            exec(f, self.context)
            function = self.context[name]
            self.code_generator.register_function(function, name)

        dsl = "## on data | show"
        c = self.code_generator(dsl)
        self.ruleset.update(rules)

    def process_all_examples(self):
        finished = False
        while not finished:
            finished = True
            for example in self.examples:
                for rule in self.ruleset.values():
                    example.apply_rule(rule)
                matrix = example.to_matrix()
                matches = matrix.matches()
                self._rules_from_matches(matches)
                anything_else_dumped = False  # Check if any matrices were updated
                finished = finished and not anything_else_dumped

    def push_example(self, dsl_string, code_string) -> None:
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
