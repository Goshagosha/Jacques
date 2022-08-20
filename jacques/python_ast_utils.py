import ast
from typing import Any, Dict, List, Tuple

LIST_INDEX = "list_index"


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

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        if isinstance(node, Pipe):
            return None
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        ArgumentExtractor(
                            arguments=self.arguments,
                            path_in_ast=self.path_in_ast + [field, LIST_INDEX],
                        ).visit(item)
            elif isinstance(value, ast.AST):
                ArgumentExtractor(
                    arguments=self.arguments, path_in_ast=self.path_in_ast + [field]
                ).visit(value)


class Arg(ast.AST):
    def __init__(self, index, examples) -> None:
        self.index = index
        self.examples = examples

    def __repr__(self) -> str:
        return f"<ARG{self.index}>"


class Lst(ast.AST):
    def __init__(self, index, examples) -> None:
        self.index = index
        self.examples = examples

    def __repr__(self) -> str:
        return f"<LST{self.index}>"


class CustomUnparser(ast._Unparser):
    def generic_visit(self, node):
        if isinstance(node, Pipe):
            self._source.append("<PIPE>")
        elif isinstance(node, Arg):
            self._source.append(str(node))
        elif isinstance(node, Lst):
            self._source.append(f"[{str(node)}]")
        else:
            return super().generic_visit(node)
