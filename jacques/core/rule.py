from __future__ import annotations
import ast
import re
from typing import TYPE_CHECKING
from jacques.ast.python_ast_utils import (
    JacquesUnparser,
    ToFunctionUnparser,
)
from jacques.ast.jacques_ast_utils import *
from jacques.core.arguments import _Argument, Choicleton
from jacques.world_knowledge import *
from pydantic import BaseModel
from loguru import logger

if TYPE_CHECKING:
    from jacques.ast.jacques_ast import DslJAST


class RuleModel(BaseModel):
    id: int
    name: str
    dsl: str
    code: str


class Rule:
    def __init__(
        self,
        code_tree: ast.AST,
        dsl_jast: DslJAST,
        code_jast: CodeJAST,
        id_provider: IdProvider,
    ) -> None:
        self.code_tree = code_tree
        self.dsl_jast = dsl_jast
        self.code_jast = code_jast
        self.id_provider = id_provider

    def to_model(self) -> RuleModel:
        return RuleModel(
            id=self.id,
            name=self.name,
            dsl=self.dsl_source,
            code=self.code_source,
        )

    def from_model(self, model: RuleModel) -> Rule:
        raise NotImplementedError
        self.id = model.id
        self.name = model.name
        self.dsl_source = model.dsl
        self.code_source = model.code
        return self

    @property
    def name(self) -> str:
        return self.dsl_jast.name

    @property
    def code_source(self) -> str:
        return JacquesUnparser().visit(self.code_tree)

    @property
    def dsl_source(self) -> str:
        return self.dsl_jast.jacques_dsl

    @property
    def nldsl_dsl(self) -> str:
        return self.dsl_jast.nldsl_dsl

    @property
    def nldsl_grammar_mods(self):
        return self.dsl_jast.nldsl_grammar_mods

    @property
    def nldsl_code(self) -> str:
        source, nldsl_code_mods = ToFunctionUnparser().to_function(self.code_tree)
        return f'{NEWLINE.join(nldsl_code_mods)}{NEWLINE}return f"{source}"'

    @property
    def regex_dsl(self) -> str:
        return self.dsl_jast.regex

    def __str__(self):
        return f"{self.__class__}\n\t{self.dsl_source}\n\t{self.code_source}"

    def __repr__(self) -> str:
        return f"{self.__class__}( {self.dsl_source} :: {self.code_source} )"


class ConditionalRule(Rule):
    def __init__(
        self,
        rule_1: Rule,
        rule_2: Rule,
    ) -> None:
        dsl_source_1 = rule_1.dsl_source
        dsl_jast_1 = rule_1.dsl_jast
        code_tree_1 = rule_1.code_tree
        code_jast_1 = rule_1.code_jast
        dsl_source_2 = rule_2.dsl_source
        dsl_jast_2 = rule_2.dsl_jast
        code_tree_2 = rule_2.code_tree
        code_jast_2 = rule_2.code_jast

        self.id_provider = rule_1.id_provider

        self.dsl_jast: DslJAST = dsl_jast_1
        choices = self.dsl_jast.merge(dsl_jast_2, self.id_provider)
        self.dsl_sources = {choices[0]: dsl_source_1, choices[1]: dsl_source_2}
        self.code_trees = {choices[0]: code_tree_1, choices[1]: code_tree_2}
        self.code_jasts = {choices[0]: code_jast_1, choices[1]: code_jast_2}
        self.choices = choices

    def add_option(
        self,
        rule: Rule,
    ) -> None:
        dsl_source = rule.dsl_source
        dsl_jast = rule.dsl_jast
        code_tree = rule.code_tree
        code_jast = rule.code_jast
        self.choices = self.dsl_jast.merge(dsl_jast, self.id_provider)
        new_choice = self.choices[-1]
        self.dsl_sources[new_choice] = dsl_source
        self.code_trees[new_choice] = code_tree
        self.code_jasts[new_choice] = code_jast

    @property
    def nldsl_code_choice(self):
        return self.dsl_jast.nldsl_code_choice

    @property
    def nldsl_code(self) -> str:
        sources = {}
        for choice in self.code_trees:
            source, nldsl_code_mods = ToFunctionUnparser().to_function(
                self.code_trees[choice]
            )
            sources[choice] = source
        source = NEWLINE
        for each in sources:
            source += f'{INDENT + NEWLINE}elif {self.nldsl_code_choice} == "{each}":{NEWLINE + INDENT}return f"{sources[each]}"'
        source = source[5:]
        return f"{NEWLINE.join(nldsl_code_mods)}{source}"

    @property
    def code_source(self) -> str:
        logger.info(self.nldsl_code)
        return self.nldsl_code

    def __str__(self):
        code_source = "\n\t".join(
            [
                JacquesUnparser().visit(self.code_trees[choice])
                for choice in self.code_trees
            ]
        )
        return f"{self.__class__}\n\t{self.dsl_source}\n\t{code_source}"

    def __repr__(self) -> str:
        code_source = "\n\t".join(
            [
                JacquesUnparser().visit(self.code_trees[choice])
                for choice in self.code_trees
            ]
        )
        return f"{self.__class__}( {self.dsl_source} :: {code_source} )"
