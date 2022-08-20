from argparse import ArgumentError
import ast
from typing import Any, TYPE_CHECKING
from jacques.jast import *
from copy import deepcopy
from jacques.jacques_member import JacquesMember


ASSIGN_COMMAND_NAME = "assign"
LOAD_COMMAND_NAME = "load"
SUBSCRIPT_COMMAND_NAME = "subscript"


class PythonParser(JacquesMember):
    def __init__(self, jacques) -> None:
        super().__init__(jacques)

    def parse(self, source_string: str) -> CodeJAST:
        entry_tree = ast.parse(source_string).body[0]
        bootstrap_jast = JastBuilder(jacques=self.jacques).visit(entry_tree)
        bootstrap_jast.inverse_depth_rec()
        if len(bootstrap_jast.children) == 0:
            return bootstrap_jast
        return bootstrap_jast.children[0]


class JastBuilder(ast.NodeVisitor):
    def __init__(
        self,
        jast: CodeJAST = None,
        jacques=None,
    ) -> None:
        if jacques is None:
            raise ArgumentError
        self.jacques = jacques
        self.encountered_objects = jacques.encountered_objects
        if jast == None:
            self.jast = CodeJAST()
            self.jast.depth = -1
        else:
            self.jast = jast
        super().__init__()

    def visit(self, node: ast.AST) -> Any:
        og_jast = self.jast
        super().visit(node)
        return og_jast

    def make_child(self, code_ast):
        new_jast = CodeJAST()
        new_jast.depth = self.jast.depth + 1
        self.jast.add_child(new_jast)
        self.jast = new_jast
        self.jast.code_ast = code_ast

    def visit_Call(self, node: ast.Call) -> Any:
        self.make_child(node)
        if isinstance(node.func, ast.Name):
            self.jast.command = node.func.id
        elif isinstance(node.func, ast.Attribute):
            self.jast.command = node.func.attr
        super().generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> Any:
        self.make_child(node)
        self.jast.command = ASSIGN_COMMAND_NAME
        super().generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        self.make_child(node)
        self.jast.command = SUBSCRIPT_COMMAND_NAME
        super().generic_visit(node)

    def visit_Name(self, node: ast.Name) -> Any:
        if isinstance(node.ctx, ast.Store):
            self.encountered_objects.append(node.id)
        elif isinstance(node.ctx, ast.Load):
            # User defined:
            if node.id in self.encountered_objects:
                self.make_child(node)
                self.jast.command = LOAD_COMMAND_NAME
            # Call to the module:
            else:
                pass
        else:
            raise NotImplementedError
