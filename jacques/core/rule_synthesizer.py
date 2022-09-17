from __future__ import annotations
import ast
from typing import TYPE_CHECKING
from jacques.ast.python_ast_utils import (
    ArgumentExtractor,
    ListIndex,
)
from jacques.core.arguments import _Argument, Dictleton, IdProvider, Singleton
from jacques.utils import key_by_value
from jacques.ast.jacques_ast_utils import *
from jacques.core.jacques_member import JacquesMember
from jacques.core.rule import Rule
from jacques.ast.python_ast_arg_replacer import ArgumentReplacer
from jacques.core.example import Example
from loguru import logger

if TYPE_CHECKING:
    from typing import List, Tuple
    from jacques.ast.jacques_ast import CodeJAST, DslJAST
    from main import Jacques


class RuleSynthesizer(JacquesMember):
    def __init__(self, jacques: Jacques) -> None:
        super().__init__(jacques=jacques)

    def from_example(self, example: Example) -> List[Rule]:
        logger.debug(f"Processing example: {example}")
        rules: List[Rule] = []
        matches = example.matches()
        logger.debug(f"Found {len(matches)} matches")
        for each in matches:
            # WARNING, similar commands with different keywords will not be parsed properly
            rule = self._from_match(*each)
            logger.info(f"Generated rule: {rule}")
            rules.append(rule)
        return rules

    def _from_match(
        self, dsl_jast: DslJAST, code_jast: CodeJAST, pipe_nodes: List[CodeJAST]
    ) -> Rule:
        logger.debug(f"Dsl jast: {dsl_jast.command}")
        logger.debug(f"Code jast: {code_jast.source_code}")
        code_ast = CodeExtractor(self.jacques).extract(code_jast, pipe_nodes)
        id_provider = IdProvider()
        for hash in dsl_jast.mapping:
            dsl_arg = dsl_jast.mapping[hash]
            code_ast, placeholder = ArgumentReplacer(dsl_arg, id_provider).replace(
                code_ast
            )
            if placeholder:
                dsl_jast.mapping[hash] = placeholder

        return Rule(
            code_tree=code_ast,
            dsl_jast=dsl_jast,
            code_jast=code_jast,
            id_provider=id_provider,
        )
