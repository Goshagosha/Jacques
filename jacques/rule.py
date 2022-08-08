from __future__ import annotations
import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from jacques.j_ast import CodeJAST, DslJAST
    from main import Jacques


class Pipe(ast.AST):
    def __init__(self, placeholding_for: ast.Call | ast.Subscript) -> None:
        self.placeholding_for = placeholding_for


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


class SubtreeIsolator(ast.NodeTransformer):
    def __init__(self, parts_of_subtree: List[ast.AST]) -> None:
        self.parts_of_subtree: List[ast.AST] = parts_of_subtree
        super().__init__()

    def visit_Call(self, node: ast.Call):
        if node not in self.parts_of_subtree:
            return Pipe(placeholding_for=node)
        return self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        if node not in self.parts_of_subtree:
            return Pipe(placeholding_for=node)
        return self.generic_visit(node)

    def generic_visit(self, node: ast.AST) -> ast.AST:
        if isinstance(node, Pipe):
            return None
        return super().generic_visit(node)


class Rule:
    def __init__(
        self,
        dsl_jast: DslJAST,
        code_jast_list: List[CodeJAST],
        more_samples: List[Tuple[DslJAST, List[CodeJAST]]],
    ) -> None:
        more_samples = [t for t in more_samples if t[0] != dsl_jast]
        # Find root CodeJAST
        # It's going to have the lowest depth ofc.
        root_codejast = code_jast_list[0]
        for each in code_jast_list:
            if each.depth < root_codejast.depth:
                root_codejast = each
        isolated_subtree: ast.AST = SubtreeIsolator(
            [jast.code_ast for jast in code_jast_list]
        ).visit(root_codejast.code_ast)
        pass

        self.rule = "<PIPE>.join(<ARG0>, how=<ARG1>, on=<LST0>)"

    def render(self, *input):
        return
        raise NotImplementedError


class RuleSynthesizer:
    def __init__(self, jacques: Jacques) -> None:
        self.jacques = jacques

    def from_matches(
        self, matches: List[Tuple[DslJAST, List[CodeJAST]]]
    ) -> Dict[str, Rule]:
        rules: Dict[str, Rule] = {}
        for each in matches:
            (name, rule) = self.__from_match(*each)
            rules[name] = rule
        return rules

    def __from_match(
        self, dsl_jast: DslJAST, code_jast_list: List[CodeJAST]
    ) -> Tuple[str, Rule]:
        dsl_command = dsl_jast.command
        more_samples = self.jacques.jast_storage.get_samples(dsl_command)
        return dsl_command, Rule(dsl_jast, code_jast_list, more_samples)
