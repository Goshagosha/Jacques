import ast, copy
from typing import Any

from click import argument
from jacques.j_ast import *
from jacques.parser.parser import Parser
from jacques.problem_knowledge import ProblemKnowledge

from jacques.utils import is_float


class PythonParser(Parser):
    class CommandBuffer:
        def __init__(self) -> None:
            self.flush()

        def flush(self):
            self.arguments = None

        def __setattr__(self, __name: str, __value: Any) -> None:
            if __value != None and self.__getattribute__(__name) != None:
                raise Exception("Trying to overwrite set attribute")
            super().__setattr__(__name, __value)

    def __init__(self, world_knowledge, problem_knowledge: ProblemKnowledge) -> None:
        self.next_subtree = None
        self.old_jast = None
        self.command_buffer = PythonParser.CommandBuffer()
        super().__init__(world_knowledge, problem_knowledge)

    def set_next_subtree(self, node):
        if node == None:
            self.next_subtree = None
        elif self.next_subtree:
            raise Exception("Found call node twice - this is not a linear program!")
        else:
            self.next_subtree = node

    def parse(self, source_string: str) -> CodeJAST:
        subtrees = []
        self.set_next_subtree(ast.parse(source_string).body[0].value)
        while self.next_subtree != None:
            processing = self.next_subtree
            self.set_next_subtree(None)
            subtree = TreeChopper(calling_parser=self).visit(processing)
            subtrees.append(subtree)

        root_jast = CodeJAST()
        self.jast = root_jast
        for subtree in subtrees:
            JastBuilder(calling_parser=self).visit(subtree)
            self.jast.code_ast = subtree
            if self.old_jast != None:
                self.old_jast.child = self.jast
            self.old_jast = self.jast
            self.jast = CodeJAST()
        return root_jast

    class Placeholder:
        def __init__(self) -> None:
            pass


class JastBuilder(ast.NodeVisitor):
    def __init__(self, calling_parser) -> None:
        self.jast = calling_parser.jast
        super().__init__()

    def visit_Call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Name):
            self.jast.command = node.func.id
        elif isinstance(node.func, ast.Attribute):
            self.jast.command = node.func.attr
        for each in node.args:
            self.jast.arguments += _resolve_argument(each)
        for each in node.keywords:
            self.jast.arguments += [StringArgument(each.arg)]
            self.jast.arguments += _resolve_argument(each.value)

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        self.jast.command = "subscript"
        self.jast.arguments += _resolve_argument(node.value)
        self.jast.arguments += _resolve_argument(node.slice)

    def generic_visit(self, node) -> Any:
        return None


class TreeChopper(ast.NodeTransformer):
    def __init__(self, calling_parser: PythonParser) -> None:
        self.calling_parser = calling_parser
        self.first_visit = True
        super().__init__()

    def visit_Call(self, node: ast.Call):
        if not self.first_visit:
            self.calling_parser.set_next_subtree(node)
            return [PythonParser.Placeholder()]
        self.first_visit = False
        return super().generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        if not self.first_visit:
            self.calling_parser.set_next_subtree(node)
            return [PythonParser.Placeholder()]
        self.first_visit = False
        return super().generic_visit(node)

    def generic_visit(self, node: ast.AST) -> ast.AST:
        if isinstance(node, PythonParser.Placeholder):
            return None
        return super().generic_visit(node)


def _resolve_argument(node) -> List[Argument]:
    if isinstance(node, ast.Constant):
        if is_float(node.value):
            return [NumberArgument(node.value)]
        else:
            return [StringArgument(str(node.value))]
    elif isinstance(node, ast.Name):
        return [KeywordArgument(node.id)]
    elif isinstance(node, ast.List):
        l = []
        for each in node.elts:
            l += _resolve_argument(each)
        return [ListArgument(l)]
    elif isinstance(node, ast.Compare):
        return [
            OperationArgument(
                *_resolve_argument(node.left),
                str(node.ops[0]),
                *_resolve_argument(node.comparators[0]),
            )
        ]
    elif isinstance(node, list):
        return [_resolve_argument(each) for each in node]
    elif isinstance(node, PythonParser.Placeholder):
        return []
    else:
        return [_resolve_argument(each) for each in ast.iter_child_nodes(node)]
