from jacques.j_ast import JAST, AstType, ListArgument
from jacques.parser.parser import Parser
import ast


class PythonParser(Parser):
    def parse(self, source_string: str) -> JAST:
        jast = JAST(AstType.CODE)
        jast_in_focus = jast
        tree = ast.parse(source_string)

        # find entry call
        call_node = tree.body[0].value

        while call_node != None:
            if isinstance(call_node.func, ast.Name):
                jast_in_focus.command = call_node.func.id
            elif isinstance(call_node.func, ast.Attribute):
                jast_in_focus.command = call_node.func.attr
            else:
                raise NotImplementedError("Unhandled Call().func type")

            for arg in call_node.args:
                if isinstance(arg, ast.Call):
                    next_call_node = arg
                elif isinstance(arg, ast.List):
                    la = ListArgument(
                        [self._resolve_non_list_argument(each) for each in arg.elts]
                    )
                    jast.arguments.append(la)
            for kw in call_node.keywords:
                if isinstance(arg, ast.Call):
                    next_call_node = arg
                elif isinstance(arg, ast.List):
                    la = ListArgument(
                        [self._resolve_non_list_argument(each) for each in arg.elts]
                    )
                    jast.arguments.append(la)
            jast.child = JAST(AstType.CODE)
            jast_in_focus = jast.child

            call_node = next_call_node
            next_call_node = None

        return jast

    def _dfs_Call_search(self, tree: ast.AST) -> ast.AST:
        layer_stack = list(ast.iter_child_nodes(tree))
        next_layer_stack = []
        for node in layer_stack:
            if isinstance(node, ast.Call):
                return node
            next_layer_stack += list(ast.iter_child_nodes(node))
