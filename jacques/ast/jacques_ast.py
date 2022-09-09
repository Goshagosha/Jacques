from __future__ import annotations
from abc import ABC, abstractmethod
from ast import AST
from typing import Dict, List

from jacques.utils import id_generator
from jacques.core.arguments import _Argument, Pipe


class JAST:
    def __init__(self) -> None:
        self.children: List[JAST] = []
        self.depth: int = None
        self.inverse_depth: int = None
        self.parent: JAST = None

    def set_parent(self, parent: JAST):
        self.parent = parent
        parent.children.append(self)

    def add_child(self, child: JAST):
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
    def __init__(self):
        self.code_ast: AST = None
        self.command = None
        super().__init__()

    def childfree_copy(self) -> CodeJAST:
        new = CodeJAST()
        new.command = self.command
        new.depth = self.depth
        new.inverse_depth = self.inverse_depth
        new.code_ast = self.code_ast
        return new


class DslJAST(JAST):
    def __init__(self):
        self.dsl_string: str = None
        self.deconstructed: list = None
        self.mapping: Dict = None
        super().__init__()

    @property
    def jacques_dsl(self) -> str:
        result = []
        for h in self.deconstructed:
            arg = self.mapping[h]
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
        for h in self.deconstructed:
            arg = self.mapping[h]
            if isinstance(arg, _Argument.Placeholder):
                result.append(arg.nldsl_dsl)
            else:
                result.append(str(arg))
        return " ".join(result)
