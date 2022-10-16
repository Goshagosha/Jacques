from __future__ import annotations
from abc import ABC, abstractmethod
from ast import AST
import re
from typing import Dict, List
from jacques.ast.python_ast_utils import JacquesUnparser

from jacques.utils import id_generator
from jacques.core.arguments import (
    _Argument,
    Choicleton,
    IdProvider,
    Listleton,
    Pipe,
    Singleton,
)


class JAST:
    def __init__(self) -> None:
        self.children: List[JAST] = []
        self.depth: int = 0
        self.inverse_depth: int = None
        self.parent: JAST = None

    def set_parent(self, parent: JAST):
        self.parent = parent
        parent.children.append(self)

    def add_child(self, child: JAST):
        child.depth = self.depth + 1
        self.children.append(child)
        child.parent = self

    def inverse_depth_rec(self):
        if len(self.children) == 0:
            self.inverse_depth = 0
        else:
            max_in_child = 0
            for child in self.children:
                child_d = child.inverse_depth_rec()
                max_in_child = max(max_in_child, child_d)
            self.inverse_depth = max_in_child + 1
        return self.inverse_depth

    def __contains__(self, other_ast) -> bool:
        other_command = other_ast.command
        if self.command == other_command:
            return True
        for child in self.children:
            if other_ast in child:
                return True
        return False

    def __iter__(self):
        yield self
        for child in self.children:
            for node in child:
                yield node


class CodeJAST(JAST):
    def __init__(self, code_ast, command, *args, **kwargs) -> None:
        self.code_ast: AST = code_ast
        self.command = command
        super().__init__(*args, **kwargs)

    @property
    def source_code(self):
        return JacquesUnparser().visit(self.code_ast)

    def childfree_copy(self) -> CodeJAST:
        new = CodeJAST(self.code_ast, self.command)
        new.depth = self.depth
        new.inverse_depth = self.inverse_depth
        return new


class DslJAST(JAST):
    def __init__(self):
        self.dsl_string: str = None
        self.deconstructed: list = None
        self.mapping: Dict = None
        super().__init__()

    def merge(self, other: DslJAST, id_provider: IdProvider) -> List[str]:
        """
        Returns:
            str: The choice keyword for new option
        """
        for i in range(len(self.deconstructed)):

            l_hash = self.deconstructed[i]
            r_hash = other.deconstructed[i]
            l_arg = self.mapping[l_hash]
            r_arg = other.mapping[r_hash]
            if isinstance(l_arg, Singleton.DSL):
                if isinstance(r_arg, _Argument.Placeholder):
                    r_arg = Singleton.DSL(r_arg.examples, -1)
                if l_arg != r_arg:
                    choicleton = Choicleton.Placeholder(l_arg, r_arg, id_provider)
                    self.mapping[l_hash] = choicleton
                    return self.mapping[l_hash].choices
            elif isinstance(l_arg, Choicleton.Placeholder):
                l_arg.add_choice(r_arg)
                return l_arg.choices

    @property
    def placeholders(self):
        return [
            arg
            for arg in self.mapping.values()
            if isinstance(arg, _Argument.Placeholder)
        ]

    @property
    def nldsl_code_choice(self) -> str:
        for h in self.deconstructed:
            arg = self.mapping[h]
            if isinstance(arg, Choicleton.Placeholder):
                return arg.nldsl_code_choice

    @property
    def jacques_dsl(self) -> str:
        result = []
        for h in self.deconstructed:
            arg = self.mapping[h]
            result.append(str(arg))
        return " ".join(result)

    @property
    def name(self) -> str:
        result = []
        for h in self.deconstructed:
            arg = self.mapping[h]
            if isinstance(arg, (_Argument.Placeholder, Pipe)):
                break
            result.append(str(arg))
        return " ".join(result)

    @property
    def command(self) -> str:
        command = []
        for h in self.deconstructed:
            arg = self.mapping[h]
            if isinstance(arg, _Argument.Placeholder):
                pass
            else:
                command.append(str(arg))
        return " ".join(command)

    @property
    def nldsl_grammar_mods(self) -> str:
        result = []
        for h in self.deconstructed:
            arg = self.mapping[h]
            if isinstance(arg, _Argument.Placeholder):
                if arg.nldsl_grammar_mod:
                    result.append(arg.nldsl_grammar_mod)
        return "\n".join(result)

    @property
    def nldsl_dsl(self) -> str:
        result = []
        list_hack = None
        for i, h in enumerate(self.deconstructed):
            arg = self.mapping[h]
            if isinstance(arg, _Argument.Placeholder):
                if isinstance(arg, Listleton.Placeholder):
                    if i < len(self.deconstructed) - 1:
                        list_hack = arg.nldsl_dsl
                    else:
                        result.append(arg.nldsl_dsl)
                elif list_hack != None and isinstance(arg, Choicleton.Placeholder):
                    hack = f"{list_hack[:-1]} {arg.nldsl_dsl}]"
                    result.append(hack)
                else:
                    result.append(arg.nldsl_dsl)
            else:
                if list_hack != None:
                    result.append(list_hack)
                    list_hack = None
                result.append(str(arg))
        return " ".join(result)

    @property
    def regex(self) -> str:
        result = []
        for h in self.deconstructed:
            arg = self.mapping[h]
            if isinstance(arg, _Argument.Placeholder):
                result.append(arg.regex)
            else:
                result.append(re.escape(str(arg)))
        return "(\s)*^" + " ".join(result) + "(\s)*$"
