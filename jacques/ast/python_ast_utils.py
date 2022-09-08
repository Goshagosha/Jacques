import ast
from typing import Any, Dict, List, Tuple
from jacques.core.arguments import _Argument, Listleton, Operaton, Pipe, Singleton


def unparse_comparator(comparator: ast.cmpop) -> str:
    CMPOPS = {
        "Eq": "==",
        "NotEq": "!=",
        "Lt": "<",
        "LtE": "<=",
        "Gt": ">",
        "GtE": ">=",
        "Is": "is",
        "IsNot": "is not",
        "In": "in",
        "NotIn": "not in",
    }
    return CMPOPS[comparator.__class__.__name__]


class ListIndex:
    def __init__(self, index):
        self.index = index


class ArgumentExtractor(ast.NodeVisitor):
    def __init__(self, arguments=None, path_in_ast=None) -> None:
        if arguments is None:
            arguments = []
        if path_in_ast is None:
            path_in_ast = []
        self.path_in_ast = path_in_ast
        self.arguments: List[Singleton.Code | Listleton.Code] = arguments
        super().__init__()

    def extract(self, node: ast.AST) -> List[_Argument]:
        super().visit(node)
        return self.arguments

    def _add_argument(self, value):
        arg = Singleton.Code(self.path_in_ast, value)
        self.arguments.append(arg)

    def _add_list(self, value):
        arg = Listleton.Code(self.path_in_ast, value)
        self.arguments.append(arg)

    def _add_comparator(self, left, comparator, right):
        operation = unparse_comparator(comparator)
        arg = Operaton.Code(self.path_in_ast, str(left), operation, str(right))
        self.arguments.append(arg)

    def visit_Constant(self, node: ast.Constant) -> Any:
        self._add_argument(node.value)

    def visit_Name(self, node: ast.Name) -> Any:
        self._add_argument(node.id)

    def visit_keyword(self, node: ast.keyword) -> Any:
        ArgumentExtractor(
            arguments=self.arguments, path_in_ast=self.path_in_ast + [node.arg]
        ).visit(node.value)

    def visit_List(self, node: List) -> Any:
        l = []
        for each in node.elts:
            if isinstance(each, ast.Constant):
                l.append(each.value)
            else:
                raise NotImplementedError
        self._add_list(l)

    def visit_Compare(self, node: ast.Compare) -> Any:
        self._add_comparator(node.left.value, node.ops[0], node.comparators[0].value)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        if isinstance(node, Pipe):
            return None
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, ast.AST):
                        ArgumentExtractor(
                            arguments=self.arguments,
                            path_in_ast=self.path_in_ast + [field, ListIndex(i)],
                        ).visit(item)
            elif isinstance(value, ast.AST):
                ArgumentExtractor(
                    arguments=self.arguments, path_in_ast=self.path_in_ast + [field]
                ).visit(value)


class CustomUnparser(ast._Unparser):
    def generic_visit(self, node):
        if isinstance(node, (Pipe, _Argument.Placeholder)):
            self._source.append(str(node))
        else:
            return super().generic_visit(node)


class ToFunctionUnparser(ast._Unparser):
    def to_function(self, node: ast.AST) -> str:
        return f"{self.visit(node)}"

    def generic_visit(self, node):
        if isinstance(node, (Pipe, _Argument.Placeholder)):
            self._source.append(node.nldsl_code)
        else:
            return super().generic_visit(node)
