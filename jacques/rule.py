from __future__ import annotations
import ast
from typing import TYPE_CHECKING, Any
from jacques.python_ast_utils import (
    ArgumentData,
    ArgumentExtractor,
    CustomUnparser,
    ListData,
    ListIndex,
    Lst,
    Arg,
)
from jacques.utils import id_generator, key_by_value, list_compare
from jacques.jast_utils import *
from jacques.jacques_member import JacquesMember

if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from jacques.jast import CodeJAST, DslJAST
    from main import Jacques


class Rule:
    def __init__(
        self,
        dsl_source: str,
        code_tree: ast.AST,
        original_dsl_jast: DslJAST,
        original_code_jast: CodeJAST,
    ) -> None:
        self.dsl_source = dsl_source
        self.code_tree = code_tree
        self.original_dsl_jast = original_dsl_jast
        self.original_code_jast = original_code_jast
        self.code_source = CustomUnparser().visit(self.code_tree)

    def unset_unknowns(self) -> Rule:
        new_dsl_source = self.dsl_source
        for h, value in self.original_dsl_jast.arguments.items():
            new_dsl_source = new_dsl_source.replace(h, value)
        return Rule(
            dsl_source=new_dsl_source,
            code_tree=self.code_tree,
            original_dsl_jast=self.original_dsl_jast,
            original_code_jast=self.original_code_jast,
        )

    def __str__(self):
        return f"{self.__class__}\n\t{self.dsl_source}\n\t{self.code_source}"

    def __repr__(self) -> str:
        return f"{self.__class__}({self.dsl_source}, {self.code_source})"


class RuleSynthesizer(JacquesMember):
    def __init__(self, jacques: Jacques) -> None:
        super().__init__(jacques=jacques)

    def from_matches(
        self, matches: List[Tuple[DslJAST, List[CodeJAST]]]
    ) -> Dict[str, Rule]:
        rules: Dict[str, Rule] = {}
        for each in matches:
            (name, rule) = self._from_match(*each)
            rules[name] = rule
        return rules

    def _from_match(
        self, dsl_jast: DslJAST, code_jast_list: List[CodeJAST]
    ) -> Tuple[str, Rule]:

        codejast_subtree = SubtreeBuilder().build(code_jast_list)
        code_ast = CodeExtractor(self.jacques).extract(codejast_subtree)

        ast_args_list = ArgumentExtractor().extract(code_ast)
        arg_id_gen = id_generator()
        list_id_gen = id_generator()
        each: ArgumentData
        for each in ast_args_list:
            # For each argument in code we have 3 cases to tackle:
            # 1. Singleton argument in DSL and Code
            # 2. List argument in DSL (recognized) and List in Code
            # 3. Singleton in DSL (did not recognize the list) and List in Code

            if isinstance(each, ArgumentData):
                hash = key_by_value(dsl_jast.mapping, each.values[0])
                if hash != None:
                    placeholder = Arg(arg_id_gen, each.values)
                    dsl_jast.mapping[hash] = placeholder
                    # Traverse the tree to the AST object to replace and replace it with the arg placeholder
                    code_ast = RuleSynthesizer._replace_in_path_with_placeholder(
                        code_ast, each.path, placeholder
                    )
            elif isinstance(each, ListData):
                for hash, argument in dsl_jast.mapping.items():
                    if isinstance(argument, list):
                        if list_compare(
                            argument, each.values[0], lambda_left=lambda x: x.pure()
                        ):
                            placeholder = Lst(list_id_gen, each.values)
                            dsl_jast.mapping[hash] = placeholder
                            code_ast = (
                                RuleSynthesizer._replace_in_path_with_placeholder(
                                    code_ast, each.path, placeholder
                                )
                            )
                            break
                    else:
                        if list_compare([argument.pure()], each.values[0]):
                            placeholder = Lst(list_id_gen, each.values)
                            dsl_jast.mapping[hash] = placeholder
                            code_ast = (
                                RuleSynthesizer._replace_in_path_with_placeholder(
                                    code_ast, each.path, placeholder
                                )
                            )
                            break
        dsl_source = dsl_jast.reconstruct()
        return dsl_jast.command, Rule(
            dsl_source=dsl_source,
            code_tree=code_ast,
            original_dsl_jast=dsl_jast,
            original_code_jast=codejast_subtree,
        )

    def _replace_in_path_with_placeholder(
        ast_tree: ast.AST, path: list, placeholder: Arg | Lst
    ) -> ast.AST:
        # If path is empty, we must be in the Name node with a load ctx:
        if not path:
            return placeholder
        attr_access = path[0]
        if len(path) >= 2:
            if isinstance(path[1], ListIndex) and attr_access != "elts":
                subtree_list = ast_tree.__getattribute__(attr_access)
                if len(subtree_list) > 1:
                    raise NotImplementedError
                subtree = subtree_list[0]
                upd = RuleSynthesizer._replace_in_path_with_placeholder(
                    subtree, path[2:], placeholder
                )
                ast_tree.__setattr__(attr_access, [upd])
        elif attr_access == "keywords":
            raise NotImplementedError
        elif attr_access == "elts":
            return placeholder
        else:
            subtree = ast_tree.__getattribute__(attr_access)
            upd = RuleSynthesizer._replace_in_path_with_placeholder(
                subtree, path[1:], placeholder
            )
            ast_tree.__setattr__(attr_access, upd)
        return ast_tree
