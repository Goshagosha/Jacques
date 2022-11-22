from __future__ import annotations
from loguru import logger
from typing import TYPE_CHECKING
from .arguments import (
    Choicleton,
    _IdProvider,
    Listleton,
)
from .jacques_member import JacquesMember
from .rule import Rule
from ..ast.python_ast_arg_replacer import ArgumentReplacer
from .example import Example

from ..ast.jacques_ast_utils import CodeExtractor

if TYPE_CHECKING:
    from typing import List
    from ..ast.jacques_ast import CodeJAST, DslJAST
    from main import Jacques


class RuleSynthesizer(JacquesMember):
    """Class for generating rules from matches."""

    def __init__(self, jacques: Jacques) -> None:
        super().__init__(jacques=jacques)

    def from_example(self, example: Example) -> List[Rule]:
        """Generate rules from an example.

        :param example: Example to generate rules from.
        :return: List of rules."""
        logger.debug(f"Processing example: {example}")
        rules: List[Rule] = []
        matches = example.matches()
        logger.debug(f"Found {len(matches)} matches")
        for each in matches:
            # WARNING, similar commands with different keywords will not be parsed properly
            rule = self._from_match(example.id, *each)
            logger.info(f"Generated rule: {rule}")
            if rule:
                rules.append(rule)
        return rules

    def _from_match(
        self,
        example_id: str,
        dsl_jast: DslJAST,
        code_jast: CodeJAST,
        pipe_nodes: List[CodeJAST],
    ) -> Rule:
        logger.debug(f"Dsl jast: {dsl_jast.command}")
        logger.debug(f"Code jast: {code_jast.source_code}")
        code_ast = CodeExtractor(self.jacques).extract(code_jast, pipe_nodes)
        id_provider = _IdProvider()
        for i, dsl_arg in enumerate(dsl_jast.deconstructed):
            try:
                code_ast, placeholder = ArgumentReplacer(
                    dsl_arg, id_provider
                ).replace(code_ast)
            except Exception:  # pylint: disable=broad-except # that's how we SHOULD handle this
                logger.error(
                    f"Error while parsing AST for\n{code_jast.source_code}\nin a match."
                )
                for each in code_jast:
                    if each not in pipe_nodes:
                        self.jacques.except_match(example_id, each.regex)
                return None
            code_jast.code_ast = code_ast
            if placeholder:
                dsl_jast.deconstructed[i] = placeholder
                if isinstance(placeholder, Choicleton.Placeholder):
                    previous = None
                    try:
                        if i > 1:
                            previous = dsl_jast.deconstructed[i - 1]
                    except IndexError:
                        pass
                    if isinstance(previous, Listleton.Placeholder):
                        previous.link_choicleton(placeholder)

        return Rule(
            dsl_jast=dsl_jast,
            code_jast=code_jast,
            id_provider=id_provider,
        )
