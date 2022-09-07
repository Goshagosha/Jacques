from __future__ import annotations
import ast
import re
from typing import TYPE_CHECKING
from jacques.ast.python_ast_utils import (
    ArgumentPlaceholder,
    CustomUnparser,
    ToFunctionUnparser,
)
from jacques.ast.jacques_ast_utils import *

if TYPE_CHECKING:
    from jacques.ast.jacques_ast import CodeJAST, DslJAST


class Rule:
    def __init__(
        self,
        dsl_source: str,
        code_tree: ast.AST,
        original_dsl_jast: DslJAST,
        original_code_jast: CodeJAST,
    ) -> None:
        self.dsl_source = dsl_source
        self.code_tree = code_tree
        self.original_dsl_jast = original_dsl_jast
        self.original_code_jast = original_code_jast
        self.code_source = CustomUnparser().visit(self.code_tree)

    def unset_unknowns(self) -> Rule:
        new_dsl_source = self.dsl_source
        for h, value in self.original_dsl_jast.arguments.items():
            new_dsl_source = new_dsl_source.replace(h, value)
        return Rule(
            dsl_source=new_dsl_source,
            code_tree=self.code_tree,
            original_dsl_jast=self.original_dsl_jast,
            original_code_jast=self.original_code_jast,
        )

    def compile(self, dsl_source: str) -> str:
        r = self.original_dsl_jast.reconstruct_to_regex()

        return dsl_source

    def generate_function(self, name, grammar) -> str:
        function_source = ToFunctionUnparser().visit(self.code_tree)
        return f'@grammar\ndef {name}(pipe, args):\n\t"""\n\tGrammar:\n\t\t{grammar}\n\t"""\n\treturn f\'{function_source}\''

    def scrap_code(self, code_source: str) -> str:
        return code_source

    def __str__(self):
        return f"{self.__class__}\n\t{self.dsl_source}\n\t{self.code_source}"

    def __repr__(self) -> str:
        return f"{self.__class__}({self.dsl_source}, {self.code_source})"
