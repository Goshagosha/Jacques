import ast
from ast import NodeTransformer
from typing import Any, Tuple
from jacques.ast.python_ast_utils import unparse_comparator, unparse_operation
from jacques.core.arguments import _Argument, Listleton, Operaton, Singleton, IdProvider


class ArgumentReplacer(NodeTransformer):
    def __init__(self, dsl_arg: _Argument.DSL, id_provider: IdProvider) -> None:
        super().__init__()
        self.dsl_arg = dsl_arg
        self.placeholder = None
        self.id_provider = id_provider

    def replace(self, node: ast.AST) -> Tuple[ast.AST, _Argument.Placeholder | None]:
        faux_node = ast.Module(body=[node])
        visited = super().visit(faux_node)
        return visited.body[0], self.placeholder

    def _match(self, value) -> bool:
        return self.dsl_arg.relaxed_equal(value)

    def _placeholder(self, value, placeholding_for) -> _Argument.Placeholder:
        if isinstance(value, list):
            if not self.placeholder:
                self.placeholder = Listleton.Placeholder(
                    self.id_provider, value, placeholding_for
                )
        else:
            if not self.placeholder:
                self.placeholder = Singleton.Placeholder(
                    self.id_provider, value, placeholding_for
                )
        return self.placeholder

    def _operaton_placeholder(self, value, placeholding_for) -> Operaton.Placeholder:
        if not self.placeholder:
            self.placeholder = Operaton.Placeholder(
                self.id_provider, value, placeholding_for
            )
        return self.placeholder

    def visit_Constant(self, node: ast.Constant) -> Any:
        if self._match(node.value):
            return self._placeholder(node.value, node)
        return super().generic_visit(node)

    def visit_Name(self, node: ast.Name) -> Any:
        if self._match(node.id):
            return self._placeholder(node.id, node)
        return super().generic_visit(node)

    def visit_alias(self, node: ast.alias) -> Any:
        if self._match(node.name):
            return self._placeholder(node.name, node)
        return super().generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> Any:
        op = unparse_comparator(node.ops[0])
        if self._match([node.left.value, op, node.comparators[0].value]):
            return self._operaton_placeholder(
                [node.left.value, op, node.comparators[0].value], node
            )
        return super().generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        op = unparse_operation(node.op)
        if self._match([node.left.value, op, node.right.value]):
            return self._operaton_placeholder(
                [node.left.value, op, node.right.value], node
            )
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
            return self._placeholder(preprocess, node)
        return super().generic_visit(node)
