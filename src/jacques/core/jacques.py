from __future__ import annotations
from lib2to3.pgen2.token import NEWLINE
from typing import Dict, List, Tuple
from .nldsl_utils.nldsl_utils import (
    generate_function,
    generate_init_statement,
)
from ..ast.parsers.dsl_parser import DslParser
from ..ast.parsers.python_parser import PythonParser
from .rule import ConditionalRule, OverridenRule, Rule
from .rule_synthesizer import RuleSynthesizer
from .example import Example
from ..utils import sanitize
from ..world_knowledge import *

from nldsl import CodeGenerator
from loguru import logger


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
    def __init__(self) -> None:
        self.encountered_objects: List[str] = []

        self.code_generator = CodeGenerator(recommend=False)
        self.examples = []
        self.exhausted_examples = []
        self.dsl_parser = DslParser(jacques=self)
        self.python_parser = PythonParser(jacques=self)
        self._rule_synthesizer = RuleSynthesizer(jacques=self)
        self.ruleset: Dict[str, Rule] = {}
        self.heuristic_on = False
        self.except_matches = {}

    def encountered(self, object):
        if object not in self.encountered_objects:
            self.encountered_objects.append(object)

    def except_match(self, example_id: str, source_code_regex: str):
        if example_id not in self.except_matches:
            self.except_matches[example_id] = [source_code_regex]
        else:
            self.except_matches[example_id].append(source_code_regex)
        logger.info("Added to exceptions:\n\t{}", source_code_regex)

    def _generate_rules(self, example: Example) -> bool:
        rules = self._rule_synthesizer.from_example(example)
        _rules = []
        for i in range(len(rules)):
            repeated = False
            for j in range(i + 1, len(rules)):
                if rules[i].__repr__() == rules[j].__repr__():
                    repeated = True
                    break
            if not repeated:
                _rules.append(rules[i])
        for rule in _rules:
            self._register_rule(rule)
        return len(rules) > 0

    def get_rule_by_name(self, name: str) -> Rule:
        try:
            return list(filter(lambda rule: rule.name == name, self.ruleset.values()))[
                0
            ]
        except IndexError:
            return None

    def _add_to_ruleset(self, rule: Rule | OverridenRule):
        if rule.id in self.ruleset:
            if isinstance(rule, OverridenRule):
                self.ruleset[rule.id] = rule
                logger.info(f"Overriden rule: {self.ruleset[rule.id]}")
                return rule
            else:
                raise ValueError
        else:
            old_rule = self.get_rule_by_name(rule.name)
            if old_rule is not None:
                try:
                    if isinstance(old_rule, ConditionalRule):
                        old_rule.add_option(rule)
                        logger.info(f"Updated rule: {self.ruleset[old_rule.id]}")
                        return old_rule
                    else:
                        self.ruleset[old_rule.id] = ConditionalRule(old_rule, rule)
                        logger.info(f"Conditional rule: {self.ruleset[old_rule.id]}")
                        return self.ruleset[old_rule.id]
                except Exception as e:
                    # If the new generated rule is the same as the old one,
                    # the old one was not applied to the matrix, so we should
                    # override the old one
                    logger.error(e)
                    logger.debug(f"Overriding rule {old_rule}")
                    self.ruleset[old_rule.id] = rule
            else:
                self.ruleset[rule.id] = rule
                return rule

    def _register_rule(self, rule: Rule | OverridenRule):
        rule = self._add_to_ruleset(rule)
        if not rule:
            return
        try:
            function = generate_function(rule)
        except SyntaxError:
            logger.error("Syntax error in rule: {}, skipping", rule)
            return
        try:
            self.code_generator.remove_function(rule.name)
            logger.debug(f'Removed old function "{rule.name}" from code generator before updating')
        except KeyError as e:
            pass
        self.code_generator.register_function(function, rule.name)

    def remove_example(self, example: Example):
        self.exhausted_examples.append(example)
        self.examples.remove(example)

    def process_all_examples(self):
        new_rules = True
        while new_rules:
            example: Example
            new_rules = False
            to_remove = []
            for example in self.examples:
                if example.is_exhausted:
                    to_remove.append(example)
                    continue
                new_rules = self._generate_rules(example) or new_rules
            for example in to_remove:
                self.remove_example(example)
        self.heuristic_on = True
        new_rules = True
        while new_rules:
            example: Example
            new_rules = False
            to_remove = []
            for example in self.examples:
                if example.is_exhausted:
                    to_remove.append(example)
                    continue
                new_rules = self._generate_rules(example) or new_rules
            for example in to_remove:
                self.remove_example(example)
        self.heuristic_on = False
        logger.info("{} rules generated.", len(self.ruleset))
        logger.info("Examples not exhausted: {}", len(self.examples))
        for example in self.examples:
            logger.info(example)
        logger.info("Excepted due to parsing errors: {}", len(self.except_matches))
        for example_id in self.except_matches:
            logger.info(filter(lambda e: e.id == example_id, self.exhausted_examples).__next__())
        logger.info("Rules:")
        for rule in self.ruleset.values():
            logger.info(rule)

    def push_init_statement(self, dsl_string: str, code_string: str) -> None:
        func = generate_init_statement(dsl_string, code_string)
        self.code_generator.register_function(func, "initialize")

    def override_rule(self, rule: OverridenRule):
        self._register_rule(rule)

    def reset(self):
        self.encountered_objects = []
        self.examples = []
        self.ruleset = {}
        self.code_generator = CodeGenerator(recommend=False)

    def push_example(self, dsl_string: str, code_string: str) -> None:
        if dsl_string.startswith(EVAL_PIPE_PREFIX):
            dsl_string = sanitize(dsl_string[len(EVAL_PIPE_PREFIX) :])
        self.examples.append(Example(self, dsl_string, code_string))

    def push_examples_from_file(self, path: str) -> None:
        buffer = Buffer()
        with open(path, "r") as file:
            for line in file.readlines():
                if line.startswith(EVAL_PIPE_PREFIX):
                    current_dsl = sanitize(line[len(EVAL_PIPE_PREFIX) :])
                    if not buffer.is_empty:
                        dsl, code = buffer.flush()
                        if dsl.startswith(DSL_INIT_STATEMENT):
                            self.push_init_statement(dsl, code)
                        else:
                            self.push_example(dsl, code)

                    buffer.push_dsl(current_dsl)
                elif line.startswith(COMMENT_PREFIX) or line == NEWLINE:
                    continue
                else:
                    buffer.push_code(line)
            if not buffer.is_empty:
                dsl, code = buffer.flush()
                if dsl.startswith(DSL_INIT_STATEMENT):
                    self.push_init_statement(dsl, code)
                else:
                    self.push_example(dsl, code)
