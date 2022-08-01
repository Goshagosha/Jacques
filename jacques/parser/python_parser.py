import ast
from ensurepip import bootstrap
from typing import Any

from jacques.j_ast import *
from jacques.parser.parser import Parser
from jacques.problem_knowledge import ProblemKnowledge

from jacques.utils import is_float


class PythonParser(Parser):
    def __init__(self, world_knowledge, problem_knowledge: ProblemKnowledge) -> None:
        super().__init__(world_knowledge, problem_knowledge)

    def parse(self, source_string: str) -> CodeJAST:
        entry_tree = ast.parse(source_string).body[0].value
        bootstrap_jast = JastBuilder().visit(entry_tree)
        if len(bootstrap_jast.children) == 0:
            return bootstrap_jast
        return bootstrap_jast.children[0]

    class Placeholder:
        def __init__(self) -> None:
            pass


class JastBuilder(ast.NodeVisitor):
    def __init__(self, jast: CodeJAST = None) -> None:
        if jast == None:
            self.jast = CodeJAST()
        else:
            self.jast = jast
        super().__init__()

    def visit(self, node: ast.AST) -> Any:
        og_jast = self.jast
        super().visit(node)
        return og_jast

    def make_child(self):
        new_jast = CodeJAST()
        self.jast.add_child(new_jast)
        self.jast = new_jast

    def visit_Call(self, node: ast.Call) -> Any:
        self.make_child()
        if isinstance(node.func, ast.Name):
            self.jast.command = node.func.id
        elif isinstance(node.func, ast.Attribute):
            self.jast.command = node.func.attr
            JastBuilder(self.jast).visit(node.func.value)
        for each in node.args:
            JastBuilder(self.jast).visit(each)
        for each in node.keywords:
            self.jast.arguments.append(StringArgument(each.arg))
            JastBuilder(self.jast).visit(each.value)

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        left = JastBuilder().visit(node.values[0]).arguments[0]
        right = JastBuilder().visit(node.values[1]).arguments[0]
        self.jast.arguments.append(ExpressionArgument(left, node.op, right))

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        self.make_child()
        self.jast.command = "subscript"
        JastBuilder(self.jast).visit(node.value)
        JastBuilder(self.jast).visit(node.slice)

    def visit_Constant(self, node: ast.Constant) -> Any:
        if is_float(node.value):
            self.jast.arguments.append(NumberArgument(node.value))
        else:
            self.jast.arguments.append(StringArgument(str(node.value)))

    def visit_Name(self, node: ast.Name) -> Any:
        self.jast.arguments.append(KeywordArgument(node.id))

    def visit_List(self, node: List) -> Any:
        for each in node.elts:
            JastBuilder(self.jast).visit(each)

    def visit_Compare(self, node: ast.Compare) -> Any:
        self.jast.arguments.append(
            OperationArgument(
                JastBuilder().visit(node.left).arguments[0],
                str(node.ops[0]),
                JastBuilder().visit(node.comparators[0]).arguments[0],
            )
        )

    def generic_visit(self, node) -> Any:
        if isinstance(node, list):
            [JastBuilder(self.jast).visit(each) for each in node]
        return None
