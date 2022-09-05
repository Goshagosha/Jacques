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


class ArgumentData:
    def __init__(self, path: List[str], examples: List, values: List) -> None:
        self.path = path
        self.examples = examples
        self.values = values

    def __add__(self, other):
        if str(self.path) != str(other.path):
            raise ValueError(
                "Can not add ArgumentData objects with different paths in parent"
            )
        else:
            new = ArgumentData(self.path, self.examples, self.values)
            new.examples.extend(other.examples)
            new.values.extend(other.values)
            return new

    def __iadd__(self, other):
        return self.__add__(other)


# TODO
class CompareData:
    def __init__(
        self, path: List[str], examples: List, left, comparator, right
    ) -> None:
        self.path = path
        self.examples = examples
        self.lefts = [left]
        self.comparators = [comparator]
        self.rights = [right]

    def values(self, index):
        return [self.lefts[index], self.comparators[index], self.rights[index]]


class ListData:
    def __init__(self, path: List[str], examples: List, values: List) -> None:
        self.path = path
        self.examples = examples
        self.values = values

    def __add__(self, other):
        if str(self.path) != str(other.path):
            raise ValueError(
                "Can not add ArgumentData objects with different paths in parent"
            )
        else:
            new = ListData(self.path, self.examples, self.values)
            new.examples.extend(other.examples)
            new.values.extend(other.values)
            return new

    def __iadd__(self, other):
        return self.__add__(other)


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

    def _add_argument(self, ast, value):
        arg = ArgumentData(self.path_in_ast, [ast], values=[value])
        self.arguments.append(arg)

    def _add_list(self, ast, value):
        arg = ListData(self.path_in_ast, [ast], values=[value])
        self.arguments.append(arg)

    def _add_comparator(self, ast, left, comparator, right):
        arg = CompareData(self.path_in_ast, [ast], left, comparator, right)
        self.arguments.append(arg)

    def visit_Constant(self, node: ast.Constant) -> Any:
        self._add_argument(node, node.value)

    def visit_Name(self, node: ast.Name) -> Any:
        self._add_argument(node, node.id)

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
        self._add_list(node, l)

    def visit_Compare(self, node: ast.Compare) -> Any:
        operation = unparse_comparator(node.ops[0])
        self._add_comparator(
            node, node.left.value, operation, node.comparators[0].value
        )

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

    def __repr__(self) -> str:
        return f"<ARG{self.index}>"


class ListPlaceholder(ast.AST):
    def __init__(self, id_generator: id_generator, examples) -> None:
        self.index = next(id_generator)
        self.examples = examples

    def __repr__(self) -> str:
        return f"<LST{self.index}>"


class ComparePlaceholder(ast.AST):
    def __init__(self, id_generator: id_generator, examples) -> None:
        self.index = next(id_generator)
        self.examples = examples

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
