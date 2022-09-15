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

if TYPE_CHECKING:
    from jacques.ast.jacques_ast import DslJAST


class Rule:
    def __init__(
        self,
        dsl_source: str,
        code_tree: ast.AST,
        dsl_jast: DslJAST,
        code_jast: CodeJAST,
    ) -> None:
        self.dsl_source = dsl_source
        self.code_tree = code_tree
        self.dsl_jast = dsl_jast
        self.code_jast = code_jast

    @property
    def name(self) -> str:
        return self.dsl_jast.name

    @property
    def code_source(self) -> str:
        return JacquesUnparser().visit(self.code_tree)

    @property
    def nldsl_dsl(self) -> str:
        return self.dsl_jast.nldsl_dsl

    @property
    def nldsl_grammar_mods(self):
        return self.dsl_jast.nldsl_grammar_mods

    @property
    def nldsl_code(self) -> str:
        source = ToFunctionUnparser().to_function(self.code_tree)
        return f'{NEWLINE.join(self.nldsl_code_mods)}{NEWLINE}return f"{source}"'

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
    ) -> None:
        self.dsl_jast: DslJAST = None
        self.dsl_sources = {}
        self.code_trees = {}
        self.code_jasts = {}
        self.choices = []


    @property
    def dsl_jast(self) -> DslJAST:
        return self.dsl_jast

    def _add_dsl_jast(self, value: DslJAST) -> None:
        if self.dsl_jast is None:
            self.dsl_jast = value
        else:
            self.choices = self.dsl_jast.merge(value)

    def add_choice(
        self,
        dsl_source: str,
        dsl_jast: DslJAST,
        code_tree: ast.AST,
        code_jast: CodeJAST,
    ):
        self._add_dsl_jast(dsl_jast)

        # nonsense
        self.dsl_source(choice) = dsl_source
        self._code_tree(choice) = code_tree
        self._code_jast(choice) = code_jast

    @property
    def nldsl_code_choice(self):
        return self.dsl_jast.nldsl_code_choice

    @property
    def nldsl_code(self) -> str:
        sources = {
            choice: ToFunctionUnparser().to_function(self.code_trees[choice])
            for choice in self.code_trees
        }
        source = NEWLINE
        for each in sources:
            source += f'{INDENT + NEWLINE}elif {self.nldsl_code_choice} == {each}:{NEWLINE + INDENT*2}return f"{sources[each]}"'
        return f"{NEWLINE.join(self.nldsl_code_mods)}{source}"
