from __future__ import annotations
import ast
from typing import TYPE_CHECKING
from jacques.ast.python_ast_utils import (
    ArgumentExtractor,
    ListIndex,
)
from jacques.core.arguments import _Argument, Dictleton, IdProvider, Singleton
from jacques.utils import key_by_value
from jacques.ast.jacques_ast_utils import *
from jacques.core.jacques_member import JacquesMember
from jacques.core.rule import Rule

if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from jacques.ast.jacques_ast import CodeJAST, DslJAST
    from main import Jacques


class RuleSynthesizer(JacquesMember):
    def __init__(self, jacques: Jacques) -> None:
        super().__init__(jacques=jacques)

    def from_matches(self, matches: List[Tuple[DslJAST, CodeJAST]]) -> Dict[str, Rule]:
        rules: Dict[str, Rule] = {}
        for each in matches:
            (name, rule) = self._from_match(*each)
            rules[name] = rule
        return rules

    def _from_match(self, dsl_jast: DslJAST, code_jast: CodeJAST) -> Tuple[str, Rule]:

        code_ast = CodeExtractor(self.jacques).extract(code_jast)
        ast_args_list = ArgumentExtractor().extract(code_ast)
        id_factory = IdProvider()
        ast_arg: _Argument.Code
        for ast_arg in ast_args_list:
            for hash in dsl_jast.mapping:
                dsl_arg = dsl_jast.mapping[hash]
                if isinstance(dsl_arg, _Argument.DSL):
                    if ast_arg.relaxed_equal(dsl_arg):
                        if isinstance(ast_arg, Dictleton.Code):
                            placeholder = ast_arg.get_placeholder(id_factory)
                            if ast_arg.lhs.relaxed_equal(dsl_arg):
                                placeholder.lhs = Singleton.Placeholder(
                                    id_factory, dsl_arg.value
                                )
                                dsl_jast.mapping[hash] = placeholder.lhs
                            else:
                                placeholder.rhs = Singleton.Placeholder(
                                    id_factory, dsl_arg.value
                                )
                                dsl_jast.mapping[hash] = placeholder.rhs
                        else:
                            placeholder = ast_arg.create_placeholder(
                                id_factory, dsl_jast.mapping[hash]
                            )

                            dsl_jast.mapping[hash] = placeholder
                            # Traverse the tree to the AST object to replace and replace it with the arg placeholder
                        code_ast = RuleSynthesizer._replace_in_path_with_placeholder(
                            code_ast, ast_arg.path, placeholder
                        )

        dsl_source = dsl_jast.jacques_dsl
        return dsl_jast.command, Rule(
            dsl_source=dsl_source,
            code_tree=code_ast,
            dsl_jast=dsl_jast,
            code_jast=code_jast,
        )

    def _replace_in_path_with_placeholder(
        ast_tree: ast.AST,
        path: list,
        placeholder: _Argument.Placeholder,
    ) -> ast.AST:
        # If path is empty, we must be in the Name node with a load ctx:
        if not path:
            return placeholder
        attr_access = path[0]
        if attr_access == "keywords":
            index = path[1].index
            assert ast_tree.keywords[index].arg == path[2]
            upd = RuleSynthesizer._replace_in_path_with_placeholder(
                ast_tree.keywords[index].value, path[3:], placeholder
            )
            ast_tree.keywords[index].value = upd
        elif attr_access == "elts":
            return placeholder
        elif len(path) >= 2 and isinstance(path[1], ListIndex):
            index = path[1].index
            subtree_list = ast_tree.__getattribute__(attr_access)
            upd = RuleSynthesizer._replace_in_path_with_placeholder(
                subtree_list[index], path[2:], placeholder
            )
            subtree_list[index] = upd
        else:
            subtree = ast_tree.__getattribute__(attr_access)
            upd = RuleSynthesizer._replace_in_path_with_placeholder(
                subtree, path[1:], placeholder
            )
            ast_tree.__setattr__(attr_access, upd)
        return ast_tree
