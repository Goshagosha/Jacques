import ast
import re
from typing import Any, Dict, List

from ..core.arguments import (
    _Argument,
    Dictleton,
    Listleton,
    Operaton,
    Pipe,
    Singleton,
    ListIndex,
)
from ast import _Precedence, NodeVisitor, iter_fields

from ..world_knowledge import NEWLINE


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


def unparse_operation(operation: ast.AST) -> str:
    OPERATIONS = {
        "Add": "+",
        "Sub": "-",
        "Mult": "*",
        "Div": "/",
        "Mod": "%",
        "Pow": "**",
        "LShift": "<<",
        "RShift": ">>",
        "BitOr": "|",
        "BitXor": "^",
        "BitAnd": "&",
        "FloorDiv": "//",
    }
    return OPERATIONS[operation.__class__.__name__]


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

    def _add_comparator(self, left, comparator, right):
        operation = unparse_comparator(comparator)
        arg = Operaton.Code(self.path_in_ast, str(left), operation, str(right))
        self.arguments.append(arg)

    def _add_operation(self, left, op, right):
        operation = unparse_operation(op)
        arg = Operaton.Code(self.path_in_ast, str(left), operation, str(right))
        self.arguments.append(arg)

    def _add_list(self, value):
        arg = Listleton.Code(self.path_in_ast, value)
        self.arguments.append(arg)

    def _add_dict(self, dict: Dict):
        arg = Dictleton.Code(self.path_in_ast, dict)
        self.arguments.append(arg)

    def visit_List(self, node: List) -> Any:
        l = []
        for each in node.elts:
            args = ArgumentExtractor().extract(each)
            if args:
                l.append(*args)
        self._add_list(l)

    def visit_Dict(self, node: ast.Dict) -> Any:
        if len(node.keys) > 1:
            raise NotImplementedError
        d = {node.keys[0].value: node.values[0].value}
        self._add_dict(d)

    def visit_Constant(self, node: ast.Constant) -> Any:
        self._add_argument(node.value)

    def visit_Name(self, node: ast.Name) -> Any:
        self._add_argument(node.id)

    def visit_alias(self, node: ast.alias) -> Any:
        self._add_argument(node.name)

    def visit_keyword(self, node: ast.keyword) -> Any:
        ArgumentExtractor(
            arguments=self.arguments, path_in_ast=self.path_in_ast + [node.arg]
        ).visit(node.value)

    def visit_Compare(self, node: ast.Compare) -> Any:
        self._add_comparator(node.left.value, node.ops[0], node.comparators[0].value)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        self._add_operation(node.left.value, node.op, node.right.value)

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


class JacquesUnparser(ast._Unparser):
    def generic_visit(self, node):
        if isinstance(node, (Pipe, _Argument.Placeholder)):
            self._source.append(str(node))
        else:
            return super().generic_visit(node)


class JacquesRegexUnparser(ast._Unparser):
    
    def visit(self, node):
        self._source = []
        encountered_placeholders = []
        super().traverse(node)
        for i, each in enumerate(self._source):
            if isinstance(each, (Pipe, _Argument.Placeholder)):
                if each.regex not in encountered_placeholders:
                    encountered_placeholders.append(each.regex)
                    self._source[i] = each.regex
                else:
                    self._source[i] = each.regex_repeated
            else:
                self._source[i] = re.escape(each)
        return "".join(self._source)

    def generic_visit(self, node):
        if isinstance(node, (Pipe, _Argument.Placeholder)):
            self._source.append(node)
        else:
            return super().generic_visit(node)


class ToFunctionUnparser(ast._Unparser):
    def __init__(self) -> None:
        super().__init__()
        self.nldsl_code_mods = []

    def to_function(self, node: ast.AST) -> str:
        result = self.visit(node)
        self.sort_code_mods()
        return result, self.nldsl_code_mods

    def sort_code_mods(self):
        result = []
        for i in range(len(self.nldsl_code_mods)):
            if "zip(*" in self.nldsl_code_mods[i]:
                result.insert(0, self.nldsl_code_mods[i])
            else:
                result.append(self.nldsl_code_mods[i])
        self.nldsl_code_mods = result

    def generic_visit(self, node):
        if isinstance(node, _Argument.Placeholder):
            self._source.append(node.nldsl_code)
            if node.nldsl_code_mod:
                self.nldsl_code_mods.extend(node.nldsl_code_mod.split(NEWLINE))
        elif isinstance(node, Pipe):
            self._source.append(node.nldsl_code)
        else:
            # escape {}

            return super().generic_visit(node)

    def visit_Dict(self, node):
        def write_key_value_pair(k, v):
            self.traverse(k)
            self.write(": ")
            self.traverse(v)

        def write_item(item):
            k, v = item
            if k is None:
                # for dictionary unpacking operator in dicts {**{'y': 2}}
                # see PEP 448 for details
                self.write("**")
                self.set_precedence(_Precedence.EXPR, v)
                self.traverse(v)
            else:
                write_key_value_pair(k, v)

        with self.delimit("{{", "}}"):
            self.interleave(
                lambda: self.write(", "), write_item, zip(node.keys, node.values)
            )


class MissingArgumentFixer(NodeVisitor):
    def __init__(self, arguments: List[_Argument.DSL | _Argument.Placeholder]) -> None:
        self.arguments = [arg.__repr__() for arg in arguments]
        super().__init__()

    def visit(self, node: ast.AST) -> ast.AST:
        for field, value in iter_fields(node):
            if (
                isinstance(value, _Argument.Placeholder)
                and value.__repr__() not in self.arguments
            ):
                node.__setattr__(field, value.placeholding_for)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if (
                        isinstance(item, _Argument.Placeholder)
                        and item.__repr__() not in self.arguments
                    ):
                        value[i] = item.placeholding_for
                    elif isinstance(item, ast.AST):
                        self.visit(item)
            elif isinstance(value, ast.AST):
                self.visit(value)

    def generic_visit(self, node):
        if isinstance(node, Pipe):
            return None
        return super().generic_visit(node)
