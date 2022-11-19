import ast
from ast import NodeVisitor
from typing import Any
from ..ast.python_ast_utils import unparse_comparator, unparse_operation
from ..core.arguments import _Argument


class Comparer(NodeVisitor):
    def __init__(self, dsl_arg: _Argument.DSL) -> None:
        super().__init__()
        self.found_matching = 0
        self.dsl_arg = dsl_arg

    def compare(self, node: ast.AST) -> int:
        super().visit(node)
        return self.found_matching

    def _match(self, value) -> bool:
        return self.dsl_arg.relaxed_equal(value)

    def found(self):
        self.found_matching += 1

    def visit_Constant(self, node: ast.Constant) -> Any:
        if self._match(node.value):
            self.found()
        return super().generic_visit(node)

    def visit_Name(self, node: ast.Name) -> Any:
        if self._match(node.id):
            self.found()
        return super().generic_visit(node)

    def visit_alias(self, node: ast.alias) -> Any:
        if self._match(node.name):
            self.found()
        return super().generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> Any:
        op = unparse_comparator(node.ops[0])
        if self._match([node.left.value, op, node.comparators[0].value]):
            self.found()
        return super().generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        op = unparse_operation(node.op)
        if self._match([node.left.value, op, node.right.value]):
            self.found()
        return super().generic_visit(node)

    def visit_List(self, node: ast.List) -> Any:
        preprocess = []
        for each in node.elts:
            if isinstance(each, ast.Constant):
                preprocess.append(each.value)
            elif isinstance(each, ast.Name):
                preprocess.append(each.id)
            else:
                preprocess.append(each)
        if self._match(preprocess):
            self.found()
        return super().generic_visit(node)
