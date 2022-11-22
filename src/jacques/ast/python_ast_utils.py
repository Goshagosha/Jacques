import ast
import re
from typing import List
from ast import _Precedence, NodeVisitor, iter_fields

from ..core.arguments import (
    _Argument,
    Pipe,
)

from ..constants import NEWLINE


def unparse_comparator(comparator: ast.cmpop) -> str:
    compare_operations = {
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
    return compare_operations[comparator.__class__.__name__]


def unparse_operation(operation: ast.AST) -> str:
    operations = {
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
    return operations[operation.__class__.__name__]


class JacquesUnparser(ast._Unparser):  # pylint: disable=protected-access
    """Unparser for python trees which renders placeholders in NLDSL friendly format."""

    def generic_visit(self, node):
        if isinstance(node, (Pipe, _Argument.Placeholder)):
            self._source.append(str(node))
            return None
        return super().generic_visit(node)


class JacquesRegexUnparser(ast._Unparser):  # pylint: disable=protected-access
    """Unparser for python trees which renders placeholders in regex."""

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
            return None
        return super().generic_visit(node)


class ToFunctionUnparser(ast._Unparser):  # pylint: disable=protected-access
    def __init__(self) -> None:
        super().__init__()
        self.nldsl_code_mods = []

    def to_function(self, node: ast.AST) -> str:
        result = self.visit(node)
        self.sort_code_mods()
        return result, self.nldsl_code_mods

    def sort_code_mods(self):
        result = []
        for code_mode in self.nldsl_code_mods:
            if "zip(*" in code_mode:
                result.insert(0, code_mode)
            else:
                result.append(code_mode)
        self.nldsl_code_mods = result

    def generic_visit(self, node):
        if isinstance(node, _Argument.Placeholder):
            self._source.append(node.nldsl_code)
            if node.nldsl_code_mod:
                self.nldsl_code_mods.extend(node.nldsl_code_mod.split(NEWLINE))
            return None
        if isinstance(node, Pipe):
            self._source.append(node.nldsl_code)
            return None
        # escape {}
        return super().generic_visit(node)

    def visit_Dict(self, node):
        # pylint: disable=invalid-name # Copied this function from ast._Unparser
        def write_key_value_pair(k, v):
            self.traverse(k)
            self.write(": ")
            self.traverse(v)

        def write_item(item):
            k, v = item
            if k is None:
                self.write("**")
                self.set_precedence(_Precedence.EXPR, v)
                self.traverse(v)
            else:
                write_key_value_pair(k, v)

        with self.delimit("{{", "}}"):
            self.interleave(
                lambda: self.write(", "),
                write_item,
                zip(node.keys, node.values),
            )


class MissingArgumentFixer(NodeVisitor):
    def __init__(
        self, arguments: List[_Argument.DSL | _Argument.Placeholder]
    ) -> None:
        self.arguments = [arg.__repr__() for arg in arguments]
        super().__init__()

    def visit(self, node: ast.AST) -> ast.AST:
        for field, value in iter_fields(node):
            if (
                isinstance(value, _Argument.Placeholder)
                and repr(value) not in self.arguments
            ):
                setattr(node, field, value.placeholding_for)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if (
                        isinstance(item, _Argument.Placeholder)
                        and repr(item) not in self.arguments
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
