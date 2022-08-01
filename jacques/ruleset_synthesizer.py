from ast import List, Tuple
import ast
from jacques.j_ast import CodeJAST, DslJAST, JastFamily
from jacques.parser.python_parser import PythonParser


class CustomUnparser(ast._Unparser):
    def generic_visit(self, node):
        if isinstance(node, PythonParser.Placeholder):
            self._source.append("<PIPE>")
        else:
            return super().generic_visit(node)

    def set_precedence(self, precedence, *nodes):
        for node in nodes:
            if isinstance(node, list):
                for each in node:
                    self._precedences[each] = precedence
            else:
                self._precedences[node] = precedence


def custom_unparse(node: ast.AST):
    return CustomUnparser().visit(node)


def generate_mock_rule(dsl_jast: DslJAST, code_jast: CodeJAST):
    string = dsl_jast.dsl_string + "\n" + custom_unparse(code_jast.code_ast)
    return string
