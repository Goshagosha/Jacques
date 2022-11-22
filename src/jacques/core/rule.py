"""This module defines the Rule class and its variations."""
from __future__ import annotations
import ast
from functools import reduce
from typing import TYPE_CHECKING, Dict, List
from uuid import uuid4 as uuid
from pydantic import BaseModel
from loguru import logger
from ..ast.python_ast_utils import (
    JacquesUnparser,
    MissingArgumentFixer,
    ToFunctionUnparser,
)

# from ..ast.jacques_ast_utils import *
from .arguments import _IdProvider
from ..constants import NEWLINE, INDENT

if TYPE_CHECKING:
    from ..ast.jacques_ast import DslJAST, CodeJAST


class RuleModel(BaseModel):
    name: str
    dsl: str
    code: str
    id: str


class OverridenRule:
    def __init__(self, name, dsl, code, rule_id: str = None) -> None:
        self.name = name
        self.dsl = dsl
        self.code = code
        self.id = rule_id if rule_id else uuid().hex

    class OverridenRuleModel(BaseModel):
        id: str
        name: str
        dsl: str
        code: str

    def to_model(self) -> OverridenRuleModel:
        return self.to_overriden_rule_model()

    def to_overriden_rule_model(self) -> OverridenRuleModel:
        return OverridenRule.OverridenRuleModel(
            id=self.id, name=self.name, dsl=self.dsl, code=self.code
        )

    def from_model(  # pylint: disable=no-self-argument # this is constructor
        model: OverridenRuleModel,
    ) -> OverridenRule:
        return OverridenRule(model.name, model.dsl, model.code, model.id)

    def __str__(self):
        return f"{self.__class__}\n\t{self.dsl}\n\t{self.code}"


class Rule:
    def __init__(
        self,
        dsl_jast: DslJAST,
        code_jast: CodeJAST,
        id_provider: _IdProvider,
        rule_id: str = None,
    ) -> None:
        self.dsl_jast = dsl_jast
        self.code_jast = code_jast
        self.id_provider = id_provider
        self.id = rule_id if rule_id else uuid().hex

    def to_model(self) -> RuleModel:
        return RuleModel(
            name=self.name,
            dsl=self.dsl_source,
            code=self.code_source,
            id=self.id,
        )

    def to_overriden_rule_model(self):
        grammar = f"{self.nldsl_dsl}\n{self.nldsl_grammar_mods}"
        code = self.nldsl_code
        if code.startswith(NEWLINE):
            code = code[len(NEWLINE) :]
        return OverridenRule.OverridenRuleModel(
            name=self.name, dsl=grammar, code=code, id=self.id
        )

    @property
    def code_tree(self) -> ast.AST:
        return self.code_jast.code_ast

    @property
    def name(self) -> str:
        return self.dsl_jast.name

    @property
    def code_source(self) -> str:
        return JacquesUnparser().visit(self.code_tree)

    @property
    def dsl_source(self) -> str:
        return self.dsl_jast.jacques_dsl

    @property
    def nldsl_dsl(self) -> str:
        return self.dsl_jast.nldsl_dsl

    @property
    def nldsl_grammar_mods(self):
        return self.dsl_jast.nldsl_grammar_mods

    @property
    def nldsl_code(self) -> str:
        source, nldsl_code_mods = ToFunctionUnparser().to_function(
            self.code_tree
        )
        return f'{NEWLINE.join(nldsl_code_mods)}{NEWLINE}return f"{source}"'

    @property
    def regex_dsl(self) -> str:
        return self.dsl_jast.regex

    @property
    def regex_code(self) -> str:
        return self.code_jast.regex

    def __str__(self):
        return f"{self.__class__}\n\t{self.dsl_source}\n\t{self.code_source}"

    def __repr__(self) -> str:
        return f"{self.__class__}( {self.dsl_source} :: {self.code_source} )"


class ConditionalRule(Rule):
    def __init__(  # pylint: disable=super-init-not-called # we intend to override
        self,
        rule_1: Rule,
        rule_2: Rule,
    ) -> None:
        dsl_source_1 = rule_1.dsl_source
        dsl_jast_1 = rule_1.dsl_jast
        code_jast_1 = rule_1.code_jast
        dsl_source_2 = rule_2.dsl_source
        dsl_jast_2 = rule_2.dsl_jast
        code_jast_2 = rule_2.code_jast

        self.id_provider = rule_1.id_provider

        self.dsl_jast: DslJAST = dsl_jast_1

        try:
            choices = self.dsl_jast.merge(dsl_jast_2, self.id_provider)
        except Exception as e:
            logger.error(f"Error merging {rule_1} and {rule_2}")
            raise e
        self.dsl_sources = {choices[0]: dsl_source_1, choices[1]: dsl_source_2}
        self.code_jasts = {choices[0]: code_jast_1, choices[1]: code_jast_2}
        self._fix_code_asts()
        self.choices = choices
        self.id = rule_1.id

    @property
    def nldsl_dsl(self) -> str:
        return self.dsl_jast.nldsl_dsl

    @property
    def regex_code(self) -> str:
        def splitter(string: str) -> List[str]:
            result = []
            next_token = ""
            for c in string:
                if c.isalpha():
                    next_token += c
                else:
                    if next_token:
                        result.append(next_token)
                        next_token = ""
                    result.append(c)
            if next_token:
                result.append(next_token)
            return result

        regexes_of_code = [
            splitter(code_jast.regex) for code_jast in self.code_jasts.values()
        ]

        def compresser(accu, regex):
            REGEX_TOKEN = "REGEX_TOKEN"
            result = []
            for i, token in enumerate(accu):
                if token == regex[i]:
                    result += [token]
                else:
                    result += [REGEX_TOKEN]
            result = [x if x != REGEX_TOKEN else "(.*)" for x in result]
            return result

        reduced = reduce(compresser, regexes_of_code)
        return "".join(reduced)

    @property
    def code_trees(self) -> Dict[str | ast.AST]:
        return {
            choice: code_jast.code_ast
            for choice, code_jast in self.code_jasts.items()
        }

    def _fix_code_asts(self) -> None:
        for choice in self.code_jasts:
            args = self.dsl_jast.placeholders
            MissingArgumentFixer(args).visit(self.code_trees[choice])

    def add_option(
        self,
        rule: Rule,
    ) -> None:
        dsl_source = rule.dsl_source
        dsl_jast = rule.dsl_jast
        code_tree = rule.code_tree
        code_jast = rule.code_jast
        self.choices = self.dsl_jast.merge(dsl_jast, self.id_provider)
        new_choice = self.choices[-1]
        self.dsl_sources[new_choice] = dsl_source
        self.code_trees[new_choice] = code_tree
        self.code_jasts[new_choice] = code_jast

    @property
    def nldsl_code_choice(self):
        return self.dsl_jast.nldsl_code_choice

    @property
    def nldsl_code(self) -> str:
        sources = {}
        accumulated_nldsl_code_mods = []
        for choice in self.code_trees:
            source, nldsl_code_mods = ToFunctionUnparser().to_function(
                self.code_trees[choice]
            )
            sources[choice] = source
            accumulated_nldsl_code_mods.extend(nldsl_code_mods)
        accumulated_nldsl_code_mods = list(set(accumulated_nldsl_code_mods))
        source = NEWLINE
        for choice, source_bit in sources.items():
            # pylint: disable=line-too-long # this is the most reliable way to handle the source-code-as-string magic
            source += f'{INDENT + NEWLINE}elif {self.nldsl_code_choice} == "{choice}":{NEWLINE + INDENT}return f"{source_bit}"'
        source = source[5:]
        return f"{NEWLINE.join(accumulated_nldsl_code_mods)}{NEWLINE}{source}"

    @property
    def code_source(self) -> str:
        logger.info(self.nldsl_code)
        return self.nldsl_code

    def __str__(self):
        code_source = "\n\t".join(
            [
                JacquesUnparser().visit(self.code_trees[choice])
                for choice in self.code_trees
            ]
        )
        return f"{self.__class__}\n\t{self.dsl_source}\n\t{code_source}"

    def __repr__(self) -> str:
        code_source = "\n\t".join(
            [
                JacquesUnparser().visit(self.code_trees[choice])
                for choice in self.code_trees
            ]
        )
        return f"{self.__class__}( {self.dsl_source} :: {code_source} )"
