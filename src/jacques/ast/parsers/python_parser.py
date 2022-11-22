import ast
from ast import iter_child_nodes
from typing import Any
from ...ast.jacques_ast import CodeJAST
from ...core.jacques_member import JacquesMember


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
        bootstrap_jast.height_rec()
        return bootstrap_jast


class JastBuilder(ast.NodeTransformer):
    def __init__(self, jacques) -> None:
        self.jacques = jacques
        self.root_jast = None
        super().__init__()

    NODES_TO_PIPE = (
        ast.Import,
        ast.ImportFrom,
        ast.Call,
        ast.Subscript,
    )
    # special cases:
    # ast.Name

    def _resolve_command_name(
        self, node: ast.AST
    ) -> str:  # pylint: disable=too-many-return-statements
        if isinstance(node, ast.Assign):
            return ASSIGN_COMMAND_NAME
        if isinstance(node, ast.Load):
            return LOAD_COMMAND_NAME
        if isinstance(node, ast.Subscript):
            return SUBSCRIPT_COMMAND_NAME
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return IMPORT_COMMAND_NAME
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
            if isinstance(node.func, ast.Attribute):
                return node.func.attr
        if isinstance(node, ast.Name):
            return LOAD_COMMAND_NAME
        raise NotImplementedError

    def visit(self, node: ast.AST) -> Any:
        self.generic_visit(node, self.root_jast)
        return self.root_jast

    def generic_visit(self, node, parent_jast=None):
        if isinstance(node, ast.AST):
            if isinstance(node, self.NODES_TO_PIPE):
                command = self._resolve_command_name(node)
                if self.root_jast is None:
                    self.root_jast = CodeJAST(node, command)
                    parent_jast = self.root_jast
                else:
                    new_jast = CodeJAST(node, command)
                    parent_jast.add_child(new_jast)
                    parent_jast = new_jast
            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    command = self._resolve_command_name(node)
                    if node.id in self.jacques.encountered_objects:
                        if self.root_jast is None:
                            self.root_jast = CodeJAST(node, command)
                            parent_jast = self.root_jast
                        else:
                            new_jast = CodeJAST(node, command)
                            parent_jast.add_child(new_jast)
                            parent_jast = new_jast
                else:
                    self.jacques.encountered(node.id)
        for child_node in iter_child_nodes(node):
            self.generic_visit(child_node, parent_jast)
        return node
