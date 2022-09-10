from __future__ import annotations
from lib2to3.pgen2.token import NEWLINE
from typing import Dict, List, Tuple
from jacques.ast.jacques_ast import CodeJAST, DslJAST
from jacques.core.nldsl_utils import generate_function, generate_init_statement
from jacques.parsers.dsl_parser import DslParser
from jacques.parsers.python_parser import PythonParser
from jacques.core.rule import Rule
from jacques.core.rule_synthesizer import RuleSynthesizer
from jacques.core.example import Example, _ExampleMatrix
from jacques.utils import sanitize
from nldsl import CodeGenerator


class Buffer:
    def __init__(self) -> None:
        self.dsl = ""
        self.code = []

    def flush(self) -> Tuple[str, str]:
        dsl = self.dsl
        code = "\n".join(self.code)
        self.dsl = ""
        self.code = []
        return dsl, code

    def push_dsl(self, line: str) -> None:
        self.dsl += line

    def push_code(self, line: str) -> None:
        line = sanitize(line)
        self.code.append(line)

    @property
    def is_empty(self) -> bool:
        return (len(self.dsl) == 0) and (len(self.code) == 0)


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

    def push_init_statement(self, dsl_string: str, code_string: str) -> None:
        func = generate_init_statement(dsl_string, code_string)
        self.code_generator.register_function(func, "initialize")

    def push_example(self, dsl_string: str, code_string: str) -> None:
        if dsl_string.startswith(self.world_knowledge.EVAL_PIPE_PREFIX):
            dsl_string = sanitize(
                dsl_string[len(self.world_knowledge.EVAL_PIPE_PREFIX) :]
            )
        self.examples.append(Example(self, dsl_string, code_string))

    def push_examples_from_file(self, path: str) -> None:
        buffer = Buffer()
        with open(path, "r") as file:

            for line in file.readlines():
                if line.startswith(self.world_knowledge.EVAL_PIPE_PREFIX):
                    current_dsl = sanitize(
                        line[len(self.world_knowledge.EVAL_PIPE_PREFIX) :]
                    )
                    if not buffer.is_empty:
                        dsl, code = buffer.flush()
                        if dsl.startswith(self.world_knowledge.DSL_INIT_STATEMENT):
                            self.push_init_statement(dsl, code)
                        else:
                            self.push_example(dsl, code)

                    buffer.push_dsl(current_dsl)
                elif (
                    line.startswith(self.world_knowledge.COMMENT_PREFIX)
                    or line == self.world_knowledge.NEWLINE
                ):
                    continue
                else:
                    buffer.push_code(line)
