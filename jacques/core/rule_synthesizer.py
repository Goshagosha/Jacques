from __future__ import annotations
import ast
from typing import TYPE_CHECKING
from jacques.ast.python_ast_utils import (
    ArgumentExtractor,
    ListIndex,
)
from jacques.core.arguments import _Argument, IdFactory
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
        id_factory = IdFactory()
        ast_arg: _Argument.Code
        for ast_arg in ast_args_list:
            hash = key_by_value(
                dsl_jast.mapping, ast_arg, lambda x, y: x.relaxed_equal(y)
            )
            if hash != None:
                placeholder = ast_arg.create_placeholder(id_factory)
                dsl_jast.mapping[hash] = placeholder
                # Traverse the tree to the AST object to replace and replace it with the arg placeholder
                code_ast = RuleSynthesizer._replace_in_path_with_placeholder(
                    code_ast, ast_arg.path, placeholder
                )

        dsl_source = dsl_jast.reconstruct()
        return dsl_jast.command, Rule(
            dsl_source=dsl_source,
            code_tree=code_ast,
            original_dsl_jast=dsl_jast,
            original_code_jast=codejast_subtree,
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
        elif len(path) >= 2:
            if isinstance(path[1], ListIndex):
                subtree_list = ast_tree.__getattribute__(attr_access)
                if len(subtree_list) > 1:
                    raise NotImplementedError
                subtree = subtree_list[0]
                upd = RuleSynthesizer._replace_in_path_with_placeholder(
                    subtree, path[2:], placeholder
                )
                ast_tree.__setattr__(attr_access, [upd])
        else:
            subtree = ast_tree.__getattribute__(attr_access)
            upd = RuleSynthesizer._replace_in_path_with_placeholder(
                subtree, path[1:], placeholder
            )
            ast_tree.__setattr__(attr_access, upd)
        return ast_tree
