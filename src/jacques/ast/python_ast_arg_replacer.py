import ast
from ast import NodeTransformer, iter_fields
from typing import Any, Tuple
from ..ast.python_ast_utils import unparse_comparator, unparse_operation
from ..core.arguments import (
    _Argument,
    Listleton,
    Operaton,
    Singleton,
    _IdProvider,
)

# pylint: disable=C0103 # python built-in modules do not conform to pep8, huh


class ArgumentReplacer(NodeTransformer):
    """Replaces the argument with a placeholder

    :param dsl_arg: the argument to replace in case of a match
    :param id_provider: the id provider to use"""

    def __init__(
        self, dsl_arg: _Argument.DSL, id_provider: _IdProvider
    ) -> None:
        super().__init__()
        self.dsl_arg = dsl_arg
        self.placeholder = None
        self.id_provider = id_provider

    def replace(
        self, node: ast.AST
    ) -> Tuple[ast.AST, _Argument.Placeholder | None]:
        """Replaces the argument with a placeholder

        :param node: Python AST to replace the argument in
        :return: updated tree and the placeholder reference or None if no match was found"""
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

    def _operaton_placeholder(
        self, value, placeholding_for
    ) -> Operaton.Placeholder:
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

    def visit_Lambda(self, node: ast.Lambda) -> Any:
        return self.generic_visit(node)

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

    def generic_visit(self, node):
        for field, old_value in iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        if not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node
