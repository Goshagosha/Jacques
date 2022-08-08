import ast
from typing import Any

from jacques.j_ast import *
from jacques.parser.parser import Parser
from copy import deepcopy
from jacques.utils import is_float


class PythonParser(Parser):
    def __init__(self, jacques) -> None:
        super().__init__(jacques)

    def parse(self, source_string: str) -> CodeJAST:
        entry_tree = ast.parse(source_string).body[0].value
        bootstrap_jast = JastBuilder().visit(entry_tree)
        bootstrap_jast.inverse_depth_rec()
        if len(bootstrap_jast.children) == 0:
            return bootstrap_jast
        return bootstrap_jast.children[0]

    class Placeholder:
        def __init__(self) -> None:
            pass


class JastBuilder(ast.NodeVisitor):
    def __init__(
        self, jast: CodeJAST = None, path_in_parent: List[str | int] = []
    ) -> None:
        if jast == None:
            self.jast = CodeJAST()
            self.jast.depth = -1
        else:
            self.jast = jast
        self.path_in_parent = deepcopy(path_in_parent)
        super().__init__()

    def visit(self, node: ast.AST) -> Any:
        og_jast = self.jast
        super().visit(node)
        return og_jast

    def make_child(self):
        new_jast = CodeJAST()
        new_jast.depth = self.jast.depth + 1
        self.jast.add_child(new_jast)
        self.jast = new_jast
        self.path_in_parent = []

    def visit_Call(self, node: ast.Call) -> Any:
        self.make_child()
        if isinstance(node.func, ast.Name):
            self.jast.command = node.func.id
        elif isinstance(node.func, ast.Attribute):
            self.jast.command = node.func.attr
            JastBuilder(jast=self.jast, path_in_parent=["func", "value"]).visit(
                node.func.value
            )
        for i, each in enumerate(node.args):
            JastBuilder(jast=self.jast, path_in_parent=["args", i]).visit(each)
        for each in node.keywords:
            JastBuilder(jast=self.jast, path_in_parent=["keywords", each.arg]).visit(
                each.value
            )
        self.jast.code_ast = node

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        JastBuilder(
            jast=self.jast, path_in_parent=self.path_in_parent + ["values", 0]
        ).visit(node.values[0])
        JastBuilder(jast=self.jast, path_in_parent=self.path_in_parent + ["op"]).visit(
            node.op
        )
        JastBuilder(
            jast=self.jast, path_in_parent=self.path_in_parent + ["values", 1]
        ).visit(node.values[1])

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        self.make_child()
        self.jast.command = "subscript"
        JastBuilder(self.jast, path_in_parent=self.path_in_parent + ["value"]).visit(
            node.value
        )
        JastBuilder(
            jast=self.jast, path_in_parent=self.path_in_parent + ["slice"]
        ).visit(node.slice)
        self.jast.code_ast = node

    def visit_Constant(self, node: ast.Constant) -> Any:
        self.jast.arguments[node.value] = deepcopy(self.path_in_parent + ["value"])

    def visit_Name(self, node: ast.Name) -> Any:
        self.jast.arguments[node.id] = self.path_in_parent + ["id"]

    def visit_List(self, node: List) -> Any:
        for i, each in enumerate(node.elts):
            JastBuilder(
                jast=self.jast, path_in_parent=self.path_in_parent + ["elts", i]
            ).visit(each)

    def visit_Compare(self, node: ast.Compare) -> Any:
        JastBuilder(
            jast=self.jast, path_in_parent=self.path_in_parent + ["left"]
        ).visit(node.left)
        JastBuilder(
            jast=self.jast, path_in_parent=self.path_in_parent + ["ops", 0]
        ).visit(node.ops[0])
        JastBuilder(
            jast=self.jast, path_in_parent=self.path_in_parent + ["comparators", 0]
        ).visit(node.comparators[0])

    def generic_visit(self, node) -> Any:
        # if isinstance(node, list):
        #     [JastBuilder(self.jast).visit(each) for each in node]
        self.jast.arguments[str(node)] = self.path_in_parent
        return None
