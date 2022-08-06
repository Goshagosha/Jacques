from __future__ import annotations
import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from jacques.j_ast import CodeJAST, DslJAST
    from main import Jacques


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
        unparsed = ast.unparse(root_codejast.code_ast)
        pass


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
