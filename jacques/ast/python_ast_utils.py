import ast
from typing import Any, Dict, List, Tuple

from jacques.utils import id_generator


def unparse_comparator(comparator: ast.cmpop) -> str:
    cmpops = {
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
    return cmpops[comparator.__class__.__name__]


class ListIndex:
    def __init__(self, index):
        self.index = index


class Pipe(ast.AST):
    def __init__(self, placeholding_for: ast.Call | ast.Subscript) -> None:
        self.placeholding_for = placeholding_for

    def __str__(self) -> str:
        return "<PIPE>"

    def to_arg(self) -> str:
        return f"{{pipe}}"


class ArgumentData:
    def __init__(self, path: List[str], value: Any) -> None:
        self.path = path
        self.value = str(value)


# TODO
class CompareData:
    def __init__(self, path: List[str], left, comparator, right) -> None:
        self.path = path
        self.left = str(left)
        self.comparator = str(comparator)
        self.right = str(right)

    def value(self):
        return f"{self.left} {self.comparator} {self.right}"


class ListData:
    def __init__(self, path: List[str], value: List) -> None:
        self.path = path
        self.value = value


class ArgumentExtractor(ast.NodeVisitor):
    def __init__(self, arguments=None, path_in_ast=None) -> None:
        if arguments is None:
            arguments = []
        if path_in_ast is None:
            path_in_ast = []
        self.path_in_ast = path_in_ast
        self.arguments: List[ArgumentData | ListData] = arguments
        super().__init__()

    def extract(self, node: ast.AST) -> List[ArgumentData]:
        super().visit(node)
        return self.arguments

    def _add_argument(self, value):
        arg = ArgumentData(self.path_in_ast, value)
        self.arguments.append(arg)

    def _add_list(self, value):
        arg = ListData(self.path_in_ast, value)
        self.arguments.append(arg)

    def _add_comparator(self, left, comparator, right):
        arg = CompareData(self.path_in_ast, left, comparator, right)
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
        operation = unparse_comparator(node.ops[0])
        self._add_comparator(node.left.value, operation, node.comparators[0].value)

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


class ArgumentPlaceholder(ast.AST):
    def __init__(self, id_generator: id_generator, examples) -> None:
        self.index = next(id_generator)
        self.examples = examples

    def to_arg(self) -> str:
        return f'{{args["arg{str(self.index)}"]}}'

    def to_dsl_arg(self) -> str:
        return f"$arg{self.index}"

    def __repr__(self) -> str:
        return f"<ARG{self.index}>"


class ListPlaceholder(ast.AST):
    def __init__(self, id_generator: id_generator, examples) -> None:
        self.index = next(id_generator)
        self.examples = examples

    def to_arg(self) -> str:
        return f'{{args["lst{str(self.index)}"]}}'

    def to_dsl_arg(self) -> str:
        return f"$lst{str(self.index)}"

    def __repr__(self) -> str:
        return f"<LST{self.index}>"


class ComparePlaceholder(ast.AST):
    def __init__(self, id_generator: id_generator, examples) -> None:
        self.index = next(id_generator)
        self.examples = examples

    def to_arg(self) -> str:
        return f'{{args["cmp{str(self.index)}"]}}'

    def to_dsl_arg(self) -> str:
        return f"$cmp{str(self.index)}"

    def __repr__(self) -> str:
        return f"<CMP{self.index}>"


class CustomUnparser(ast._Unparser):
    def generic_visit(self, node):
        if isinstance(node, Pipe):
            self._source.append("<PIPE>")
        elif isinstance(node, (ArgumentPlaceholder, ComparePlaceholder)):
            self._source.append(str(node))
        elif isinstance(node, ListPlaceholder):
            self._source.append(f"[{str(node)}]")
        else:
            return super().generic_visit(node)


class ToFunctionUnparser(ast._Unparser):
    def to_function(self, node: ast.AST) -> str:
        return f"{self.visit(node)}"

    def generic_visit(self, node):
        if isinstance(
            node, (ArgumentPlaceholder, ComparePlaceholder, Pipe, ListPlaceholder)
        ):
            self._source.append(node.to_arg())
        else:
            return super().generic_visit(node)
