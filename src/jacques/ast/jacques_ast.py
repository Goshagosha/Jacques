from __future__ import annotations
from ast import AST
import re
from typing import List
from ..ast.python_ast_utils import JacquesRegexUnparser, JacquesUnparser

from ..core.arguments import (
    _Argument,
    Choicleton,
    _IdProvider,
    Listleton,
    Pipe,
    Singleton,
)


class JAST:  # pylint: disable=no-member # it's an abstract class with some members being @property
    """The core concept is described in the original paper. This class is to be subclassed for each language."""

    def __init__(self) -> None:
        self.children: List[JAST] = []
        self.depth: int = 0
        self.height: int = None
        self.parent: JAST = None

    def set_parent(self, parent: JAST):
        """Set the parent of this node and all its children."""
        self.parent = parent
        parent.children.append(self)

    def add_child(self, child: JAST):
        """Add a child to this node."""
        child.depth = self.depth + 1
        self.children.append(child)
        child.parent = self

    def height_rec(self):
        """Recursively calculate the height of all nodes in the tree.

        :return: The height of this node."""
        if len(self.children) == 0:
            self.height = 0
        else:
            max_in_child = 0
            for child in self.children:
                child_d = child.height_rec()
                max_in_child = max(max_in_child, child_d)
            self.height = max_in_child + 1
        return self.height

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
    """JAST subclass for python code ASTs.

    :param code_ast: The python AST node.
    :param command: The command called by original python AST node."""

    def __init__(self, code_ast, command, *args, **kwargs) -> None:
        self.code_ast: AST = code_ast
        self.command = command
        super().__init__(*args, **kwargs)

    @property
    def source_code(self):
        """
        :return: The source code of AST this node."""
        return JacquesUnparser().visit(self.code_ast)

    def childfree_copy(self) -> CodeJAST:
        """
        :return: A copy of this node without children."""
        new = CodeJAST(self.code_ast, self.command)
        new.depth = self.depth
        new.height = self.height
        return new

    @property
    def regex(self):
        """
        Unparse code AST into a regex with placeholders replaced with their respective regex patterns.
        :return: Regex string."""
        return JacquesRegexUnparser().visit(self.code_ast)


class DslJAST(JAST):
    """JAST subclass for DSL queries.

    :param dsl_string: The DSL query string.
    :param command: The command called by original DSL query."""

    def __init__(self):
        self.dsl_string: str = None
        self.deconstructed: list = []
        super().__init__()

    def merge(
        self, other: DslJAST, id_provider: _IdProvider
    ) -> List[str] | None:
        """Merge two DSL trees of the same format, detecting mismatch in the relevant keyword and rendering it as a Choicleton placeholder.

        :param other: The other DSL query.
        :param id_provider: The id provider to use for generating new ids.
        :return: Choice keywords produced as a result of a merge."""
        for i, l_arg in enumerate(self.deconstructed):
            r_arg = other.deconstructed[i]
            previous = None
            try:
                if i > 1:
                    previous = self.deconstructed[i - 1]
            except IndexError:
                pass
            if isinstance(l_arg, Singleton.DSL):
                if isinstance(r_arg, _Argument.Placeholder):
                    r_arg = Singleton.DSL(r_arg.examples, -1)
                if l_arg != r_arg:
                    choicleton = Choicleton.Placeholder(
                        l_arg, r_arg, id_provider
                    )
                    self.deconstructed[i] = choicleton
                    if isinstance(previous, Listleton.Placeholder):
                        previous.link_choicleton(choicleton)
                    return self.deconstructed[i].choices
            elif isinstance(l_arg, Choicleton.Placeholder):
                l_arg.add_choice(r_arg)
                if isinstance(previous, Listleton.Placeholder):
                    previous.link_choicleton(choicleton)
                return l_arg.choices
        return None

    @property
    def placeholders(self):
        """Get all placeholders in this DSL JAST.

        :return: List of placeholders."""
        return [
            arg
            for arg in self.deconstructed
            if isinstance(arg, _Argument.Placeholder)
        ]

    @property
    def nldsl_code_choice(self) -> str:
        for arg in self.deconstructed:
            if isinstance(arg, Choicleton.Placeholder):
                return arg.nldsl_code_choice

    @property
    def jacques_dsl(self) -> str:
        result = []
        for arg in self.deconstructed:
            result.append(str(arg))
        return " ".join(result)

    @property
    def name(self) -> str:
        result = []
        for arg in self.deconstructed:
            if isinstance(arg, (_Argument.Placeholder, Pipe)):
                break
            result.append(str(arg))
        return " ".join(result)

    @property
    def command(self) -> str:
        command = []
        for arg in self.deconstructed:
            if isinstance(arg, _Argument.Placeholder):
                pass
            else:
                command.append(str(arg))
        return " ".join(command)

    @property
    def nldsl_grammar_mods(self) -> str:
        result = []
        for arg in self.deconstructed:
            if isinstance(arg, _Argument.Placeholder):
                if arg.nldsl_grammar_mod:
                    result.append(arg.nldsl_grammar_mod)
        return "\n".join(result)

    @property
    def nldsl_dsl(self) -> str:
        result = []
        for arg in self.deconstructed:
            if isinstance(arg, _Argument.Placeholder):
                if isinstance(arg, Choicleton.Placeholder):
                    if arg.linked:
                        continue
                result.append(arg.nldsl_dsl)
            else:
                result.append(str(arg))
        return " ".join(result)

    @property
    def regex(self) -> str:
        result = []
        for arg in self.deconstructed:
            if isinstance(arg, _Argument.Placeholder):
                result.append(arg.regex)
            else:
                result.append(re.escape(str(arg)))
        return r"(\s)*^" + " ".join(result) + r"(\s)*$"
