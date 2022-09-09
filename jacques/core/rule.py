from __future__ import annotations
import ast
import re
from typing import TYPE_CHECKING
from jacques.ast.python_ast_utils import (
    CustomUnparser,
    ToFunctionUnparser,
)
from jacques.ast.jacques_ast_utils import *

if TYPE_CHECKING:
    from jacques.ast.jacques_ast import DslJAST


class Rule:
    def __init__(
        self,
        dsl_source: str,
        code_tree: ast.AST,
        original_dsl_jast: DslJAST,
    ) -> None:
        self.dsl_source = dsl_source
        self.code_tree = code_tree
        self.dsl_jast = original_dsl_jast

    @property
    def name(self) -> str:
        return self.dsl_jast.command

    @property
    def code_source(self) -> str:
        return CustomUnparser().visit(self.code_tree)

    @property
    def nldsl_dsl(self) -> str:
        return self.dsl_jast.nldsl_dsl

    @property
    def nldsl_grammar_mods(self):
        return self.dsl_jast.nldsl_grammar_mods

    @property
    def nldsl_code(self) -> str:
        return ToFunctionUnparser().to_function(self.code_tree)

    def __str__(self):
        return f"{self.__class__}\n\t{self.dsl_source}\n\t{self.code_source}"

    def __repr__(self) -> str:
        return f"{self.__class__}({self.dsl_source}, {self.code_source})"
