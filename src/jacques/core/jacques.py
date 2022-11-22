from __future__ import annotations
from typing import Dict, List, Tuple
from nldsl import CodeGenerator
from loguru import logger

from .nldsl_utils import (  # pylint: disable=import-error, no-name-in-module # something is wrong with pylint
    generate_function,
    generate_init_statement,
    generate_source_from_ruleset,
)
from ..ast.parsers.dsl_parser import DslParser
from ..ast.parsers.python_parser import PythonParser
from .rule import ConditionalRule, OverridenRule, Rule
from .rule_synthesizer import RuleSynthesizer
from .example import Example
from ..utils import sanitize
from .. import constants


class _Buffer:
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


class Jacques:  # pylint: disable=too-many-instance-attributes # main class
    """The core class of the package."""

    def __init__(self) -> None:
        self.encountered_objects: List[str] = []

        self.code_generator = CodeGenerator(recommend=False)
        self.examples = []
        self.exhausted_examples = []
        self.dsl_parser = DslParser(jacques=self)
        self.python_parser = PythonParser(jacques=self)
        self._rule_synthesizer = RuleSynthesizer(jacques=self)
        self.ruleset: Dict[str, Rule] = {}
        self.cross_compare_on = False
        self.except_matches = {}

    def encountered(self, obj):
        """Register an object name as encountered.

        :param obj: The object name to register."""
        if obj not in self.encountered_objects:
            self.encountered_objects.append(obj)

    def except_match(self, example_id: str, source_code_regex: str):
        """Add a regex to the list of exceptions for the given example.

        :param example_id: The id of the example to add the exception to.
        :param source_code_regex: The regex to add to the list of exceptions."""
        if example_id not in self.except_matches:
            self.except_matches[example_id] = [source_code_regex]
        else:
            self.except_matches[example_id].append(source_code_regex)
        logger.info("Added to exceptions:\n\t{}", source_code_regex)

    def _generate_rules(self, example: Example) -> bool:
        rules = self._rule_synthesizer.from_example(example)
        _rules = []
        for i, rule in enumerate(rules):
            repeated = False
            for j in range(i + 1, len(rules)):
                if repr(rule) == repr(rules[j]):
                    repeated = True
                    break
            if not repeated:
                _rules.append(rule)
        for rule in _rules:
            self._register_rule(rule)
        return len(rules) > 0

    def get_rule_by_name(self, name: str) -> Rule:
        """Get a rule by its name.

        :param name: The name of the rule to get.
        :return: The rule with the given name."""
        try:
            return list(
                filter(lambda rule: rule.name == name, self.ruleset.values())
            )[0]
        except IndexError:
            return None

    def _add_to_ruleset(self, rule: Rule | OverridenRule):
        if rule.id in self.ruleset:
            if isinstance(rule, OverridenRule):
                self.ruleset[rule.id] = rule
                logger.info(f"Overriden rule: {self.ruleset[rule.id]}")
                return rule
            raise ValueError
        old_rule = self.get_rule_by_name(rule.name)
        if old_rule is not None:
            try:
                if isinstance(old_rule, ConditionalRule):
                    old_rule.add_option(rule)
                    logger.info(f"Updated rule: {self.ruleset[old_rule.id]}")
                    return old_rule
                self.ruleset[old_rule.id] = ConditionalRule(old_rule, rule)
                logger.info(f"Conditional rule: {self.ruleset[old_rule.id]}")
                return self.ruleset[old_rule.id]
            except Exception as exc:
                # If the new generated rule is the same as the old one,
                # the old one was not applied to the matrix, so we should
                # override the old one
                logger.error(exc)
                logger.debug(f"Overriding rule {old_rule}")
                self.ruleset[old_rule.id] = rule
                return rule
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
            logger.debug(
                f'Removed old function "{rule.name}" from code generator before updating'
            )
        except KeyError:
            pass
        self.code_generator.register_function(function, rule.name)

    def export_rules(self, filename: str = "rules_exported.py"):
        """Export the ruleset to a file.

        :param filename: The name of the file to export the ruleset to."""
        source = generate_source_from_ruleset(self.ruleset.values())
        with open(filename, "w", encoding="utf-8") as file:
            file.write(source)

    def remove_example(self, example: Example):
        """Remove an example from the list of examples.

        :param example: The example to remove."""
        self.exhausted_examples.append(example)
        self.examples.remove(example)

    def process_all_examples(self):
        """Process all examples and extract rules from them. This method is to be called after providing all desired examples."""
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
        self.cross_compare_on = True
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
        self.cross_compare_on = False
        logger.info("{} rules generated.", len(self.ruleset))
        logger.info("Examples not exhausted: {}", len(self.examples))
        for example in self.examples:
            logger.info(example)
        logger.info(
            "Excepted due to parsing errors: {}", len(self.except_matches)
        )
        for example_id in self.except_matches:
            logger.info(
                next(
                    filter(
                        lambda e: e.id == example_id, self.exhausted_examples
                    )
                )
            )
        logger.info("Rules:")
        for rule in self.ruleset.values():
            logger.info(rule)

    def push_init_statement(self, dsl_string: str, code_string: str) -> None:
        func = generate_init_statement(dsl_string, code_string)
        self.code_generator.register_function(func, "initialize")

    def override_rule(self, rule: OverridenRule):
        """Override a rule. Immediately registers it with code generator.

        :param rule: The rule to override."""
        self._register_rule(rule)

    def reset(self):
        """Reset the ruleset, code generator, and all of Jacque runtime memory."""
        self.encountered_objects = []
        self.examples = []
        self.ruleset = {}
        self.code_generator = CodeGenerator(recommend=False)
        self.except_matches = {}
        self.cross_compare_on = False
        self.exhausted_examples = []

    def push_example(self, dsl_string: str, code_string: str) -> None:
        """Push an example to the list of examples.

        :param dsl_string: The DSL string of the example.
        :param code_string: The code string of the example."""
        if dsl_string.startswith(constants.EVAL_PIPE_PREFIX):
            dsl_string = sanitize(dsl_string[len(constants.EVAL_PIPE_PREFIX) :])
        self.examples.append(Example(self, dsl_string, code_string))

    def push_examples_from_file(self, path: str) -> None:
        """Push examples from a file.

        :param path: The path to the file to push examples from.
        :raises FileNotFoundError: If the file does not exist."""
        buffer = _Buffer()
        with open(path, "r", encoding="utf-8") as file:
            for line in file.readlines():
                if line.startswith(constants.EVAL_PIPE_PREFIX):
                    current_dsl = sanitize(
                        line[len(constants.EVAL_PIPE_PREFIX) :]
                    )
                    if not buffer.is_empty:
                        dsl, code = buffer.flush()
                        if dsl.startswith(constants.DSL_INIT_STATEMENT):
                            self.push_init_statement(dsl, code)
                        else:
                            self.push_example(dsl, code)

                    buffer.push_dsl(current_dsl)
                elif (
                    line.startswith(constants.COMMENT_PREFIX)
                    or line == constants.NEWLINE
                ):
                    continue
                else:
                    buffer.push_code(line)
            if not buffer.is_empty:
                dsl, code = buffer.flush()
                if dsl.startswith(constants.DSL_INIT_STATEMENT):
                    self.push_init_statement(dsl, code)
                else:
                    self.push_example(dsl, code)
