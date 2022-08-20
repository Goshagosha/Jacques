from __future__ import annotations
import ast
from typing import TYPE_CHECKING, Any
from jacques.python_ast_utils import (
    ArgumentData,
    ArgumentExtractor,
    CustomUnparser,
    ListData,
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
        dsl_jast: DslJAST,
        code_jast_list: List[CodeJAST],
        more_samples: List[Tuple[DslJAST, CodeJAST]],
    ) -> None:
        self.codejast_subtree = SubtreeBuilder().build(code_jast_list)
        code_samples = [self.codejast_subtree]
        dsl_samples = [dsl_jast]

        # filter out the main one we passed as a reference:
        more_samples = [t for t in more_samples if t[0] != dsl_jast]
        # isolate trees from other examples:
        for dj, cj in more_samples:
            for each in cj:
                extracted = clone_matched(target=each, reference=self.codejast_subtree)
                if extracted != None:
                    code_samples.append(extracted)
                    dsl_samples.append(dj)
        # Convert codejasts to python asts
        code_samples = [CodeExtractor().extract(cj) for cj in code_samples]
        # Extract arguments from all the samples, and merge them into a single list:
        all_samples_merged_arguments = {}
        for sample in code_samples:
            args_list = ArgumentExtractor().extract(sample)
            each: ArgumentData
            for each in args_list:
                NO_PATH = "no_path"
                key = NO_PATH if not each.path else str(each.path)
                if key in all_samples_merged_arguments.keys():
                    all_samples_merged_arguments[key] += each
                else:
                    all_samples_merged_arguments[key] = each
        # Convert to list cause we don't need dict magic
        all_samples_merged_arguments = list(all_samples_merged_arguments.values())

        arg_id_gen = id_generator()
        list_id_gen = id_generator()
        self.rule_code = code_samples[0]
        self.rule_dsl_source = dsl_samples[0].dsl_string
        each: ArgumentData
        for each in all_samples_merged_arguments:
            if isinstance(each, ArgumentData):
                k = key_by_value(dsl_jast.arguments, each.values[0])
                if k != None:
                    placeholder = Arg(next(arg_id_gen), each.values)
                    self.rule_dsl_source = self.rule_dsl_source.replace(
                        k, str(placeholder)
                    )
                    # Navigate to the AST object to replace and replace it with the arg placeholder
                    self.rule_code = Rule.replace_in_path_with_placeholder(
                        self.rule_code, each.path, placeholder
                    )
            elif isinstance(each, ListData):
                for hash, argument in dsl_jast.arguments.items():
                    if isinstance(argument, list):
                        if list_compare(argument, each.values[0]):
                            placeholder = Lst(next(list_id_gen), each.values)
                            self.rule_dsl_source = self.rule_dsl_source.replace(
                                hash, str(placeholder)
                            )
                            self.rule_code = Rule.replace_in_path_with_placeholder(
                                self.rule_code, each.path, placeholder
                            )
                            break
                    else:
                        if list_compare([argument], each.values[0]):
                            placeholder = Lst(next(list_id_gen), each.values)
                            self.rule_dsl_source = self.rule_dsl_source.replace(
                                hash, str(placeholder)
                            )
                            self.rule_code = Rule.replace_in_path_with_placeholder(
                                self.rule_code, each.path, placeholder
                            )
                            break
        self.rule_code_source = CustomUnparser().visit(self.rule_code)

    def replace_in_path_with_placeholder(
        ast_tree: ast.AST, path: list, placeholder: Arg | Lst
    ) -> ast.AST:
        # If path is empty, we must be in the Name node with a load ctx:
        if not path:
            return placeholder
        attr_access = path[0]
        if attr_access == "args":
            # Quick n dirty presumption that every function we see will only have one args[]
            if len(ast_tree.args) > 1:
                # Something failed about design logic if we got here
                raise ValueError
            subtree = ast_tree.args[0]
            upd = Rule.replace_in_path_with_placeholder(subtree, path[2:], placeholder)
            ast_tree.__setattr__(attr_access, [upd])
        elif attr_access == "keywords":
            raise NotImplementedError
        elif attr_access == "elts":
            if not isinstance(placeholder, Lst):
                # Something failed about design logic if we got here
                raise ValueError
            return placeholder
        else:
            subtree = ast_tree.__getattribute__(attr_access)
            upd = Rule.replace_in_path_with_placeholder(subtree, path[1:], placeholder)
            ast_tree.__setattr__(attr_access, upd)
        return ast_tree


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
        dsl_command = dsl_jast.command
        more_samples = self.jacques.jast_storage.get_samples(dsl_command)
        return dsl_command, Rule(dsl_jast, code_jast_list, more_samples)
