import ast, copy
from jacques.j_ast import *
from jacques.parser.parser import Parser
from jacques.problem_knowledge import ProblemKnowledge

from jacques.utils import is_float


class PythonParser(Parser):
    def __init__(self, world_knowledge, problem_knowledge: ProblemKnowledge) -> None:
        self.next_call_node = None
        self.jast_in_focus = None
        super().__init__(world_knowledge, problem_knowledge)

    def _set_next_call_node(self, node):
        if self.next_call_node:
            raise Exception("Found call node twice - this is not a linear program!")
        self.next_call_node = node

    def parse(self, source_string: str) -> CodeJAST:
        jast = CodeJAST()
        self.jast_in_focus = jast
        tree = ast.parse(source_string)

        # find entry call
        call_node = tree.body[0].value

        while call_node != None:
            self.jast_in_focus.code_ast = copy.deepcopy(call_node)
            self._infer_command_name(call_node)
            if isinstance(call_node, ast.Call):
                for arg in call_node.args:
                    self.jast_in_focus.arguments += self._resolve_argument(arg)
                # keywords we flatten
                for kw in call_node.keywords:
                    self.jast_in_focus.arguments += [KeywordArgument(kw.arg)]
                    self.jast_in_focus.arguments += self._resolve_argument(kw.value)
            elif isinstance(call_node, ast.Subscript):
                self.jast_in_focus.arguments += self._resolve_argument(call_node.value)
                self.jast_in_focus.arguments += self._resolve_argument(call_node.slice)
            else:
                raise NotImplementedError

            call_node = self.next_call_node
            self.next_call_node = None
            if call_node:
                self.jast_in_focus.child = CodeJAST()
                self.jast_in_focus = self.jast_in_focus.child

        return jast

    def _infer_command_name(self, node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                self.jast_in_focus.command = node.func.id
            elif isinstance(node.func, ast.Attribute):
                self.jast_in_focus.command = node.func.attr
                self.jast_in_focus.arguments += self._resolve_argument(node.func.value)
            else:
                raise NotImplementedError("Unhandled Call().func type")
        elif isinstance(node, ast.Subscript):
            self.jast_in_focus.command = "subscript"
        else:
            raise NotImplementedError

    def _resolve_argument(self, node) -> List[Argument]:
        if isinstance(node, (ast.Subscript, ast.Call)):
            self._set_next_call_node(node)
        elif isinstance(node, ast.Constant):
            if is_float(node.value):
                return [NumberArgument(node.value)]
            else:
                return [StringArgument(str(node.value))]
        elif isinstance(node, ast.Name):
            return [KeywordArgument(node.id)]
        elif isinstance(node, ast.List):
            l = []
            for each in node.elts:
                l += self._resolve_argument(each)
            return [ListArgument(l)]
        elif isinstance(node, ast.Compare):
            return [
                OperationArgument(
                    *self._resolve_argument(node.left),
                    str(node.ops[0]),
                    *self._resolve_argument(node.comparators[0]),
                )
            ]
        # we could handle this, but let's just try to collaps unknown:
        # elif isinstance(node, ast.Subscript):
        else:
            return [self._resolve_argument(each) for each in ast.iter_child_nodes(node)]
        return []
