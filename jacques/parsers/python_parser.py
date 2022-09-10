import ast
from typing import Any
from jacques.ast.jacques_ast import *
from jacques.core.jacques_member import JacquesMember


ASSIGN_COMMAND_NAME = "assign"
LOAD_COMMAND_NAME = "load"
SUBSCRIPT_COMMAND_NAME = "subscript"
IMPORT_COMMAND_NAME = "import"


class PythonParser(JacquesMember):
    def __init__(self, jacques) -> None:
        super().__init__(jacques)

    def parse(self, source_string: str) -> CodeJAST:
        entry_tree = ast.parse(source_string).body[0]
        bootstrap_jast = JastBuilder(jacques=self.jacques).visit(entry_tree)
        bootstrap_jast.inverse_depth_rec()
        return bootstrap_jast


# TODO Change JastBuilder
class JastBuilder(ast.NodeVisitor):
    def __init__(
        self,
        jast: CodeJAST = None,
        jacques=None,
    ) -> None:
        self.jacques = jacques
        self.encountered_objects = jacques.encountered_objects
        self.root_jast = None
        if jast == None:
            self.jast = CodeJAST()
            self.jast.depth = -1
        else:
            self.jast = jast
        super().__init__()

    def visit(self, node: ast.AST) -> Any:
        super().visit(node)
        return self.root_jast

    def make_child(self, code_ast):
        new_jast = CodeJAST()
        new_jast.depth = self.jast.depth + 1
        self.jast.add_child(new_jast)
        if not self.root_jast:
            self.root_jast = new_jast
        self.jast = new_jast
        self.jast.code_ast = code_ast

    def visit_alias(self, node: ast.alias) -> Any:
        if node.asname:
            self.encountered_objects.append(node.asname)
        else:
            self.encountered_objects.append(node.name)

    def visit_Import(self, node: ast.Import) -> Any:
        self.make_child(node)
        self.jast.command = IMPORT_COMMAND_NAME
        super().generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        self.make_child(node)
        self.jast.command = IMPORT_COMMAND_NAME
        super().generic_visit(node)

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
