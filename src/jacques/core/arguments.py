"""This module provides abstract base classes that are to be overriden if one wishes to cover new argument types. Also it contains specific implementations for most common cases."""
from abc import ABC, abstractmethod
from ast import AST
import ast
from typing import Any
from ..utils import id_generator, is_float


class _IdProvider:  # pylint: disable=too-few-public-methods # it's a generator
    def __init__(self) -> None:
        ...

    def __getattribute__(self, __name: str) -> Any:
        if __name.endswith("_id_gen"):
            try:
                return super().__getattribute__(__name)
            except AttributeError:
                self.__setattr__(__name, id_generator())
                return super().__getattribute__(__name)
        else:
            return super().__getattribute__(__name)


class _ListIndex:  # pylint: disable=too-few-public-methods # it's a dataclass
    def __init__(self, index):
        self.index = index


class _Argument(
    ABC
):  # pylint: disable=too-few-public-methods # it's an abstract base dataclass
    class DSL(ABC):
        """Abstract class for DSL arguments. Extend it to add new formats of DSL arguments.
        Must implement relaxed_equal method.
        Must implement __str__ method.
        :param value: value of the argument
        :param index_in_parent: index of the argument in the parent list"""

        def __init__(self, value: Any, index_in_parent: int):
            self.value = value
            self.index_in_parent = index_in_parent

        @abstractmethod
        def __str__(self) -> str:
            ...

        @abstractmethod
        def relaxed_equal(self, other) -> bool:
            """Must return True if other is matches self to a reasonable extent

            :param other: the value to compare to"""

        def __eq__(self, __o: object) -> bool:
            if isinstance(__o, str):
                return self.value == __o
            elif isinstance(__o, _Argument.Placeholder):
                return self.value == __o.examples
            return self.value == __o.value

    class Placeholder(ABC, AST):
        """Abstract class for placeholders. Extend it to add new formats of placeholders.

        :param examples: examples of the placeholder
        :param placeholding_for: the AST node that the placeholder is for
        :param id_factory: the factory that provides the id generator for the placeholder
        :base_shorthand: the shorthand of the placeholder. Is a static field that should be overridden in subclasses"""

        base_shorthand: str

        def _id_generator_ref(self, factory: _IdProvider) -> id_generator:
            generator_name = (
                self.__class__.__qualname__.split(".", maxsplit=1)[0].lower()
                + "_id_gen"
            )
            return getattr(factory, generator_name)

        def __init__(
            self, id_factory: _IdProvider, examples, placeholding_for: ast.AST
        ):
            id_generator = self._id_generator_ref(  # pylint: disable=redefined-outer-name # that's what this generator is for
                id_factory
            )
            self.id = next(id_generator)
            self.examples = examples
            self.placeholding_for = placeholding_for

        @property
        def shorthand(self):
            """The shorthand of the placeholder. With a given placeholder e.g. INT and id==0, the shorthand is INT0. Used to distinguish placeholders in rules, and render them to logs or to register in NLDSL."""
            return self.base_shorthand + str(self.id)

        @property
        def nldsl_grammar_mod(self):
            """The grammar modification for the placeholder. Implement if the argument requires important NLDSL grammar logic."""

        @property
        def nldsl_code_mod(self):
            """The code modification for the placeholder. Implement if the argument requires important preprocessing in NLDSL function."""

        @property
        @abstractmethod
        def nldsl_code(self) -> str:
            """How the placeholder should be rendered in NLDSL function, in the code section."""
            ...

        @property
        @abstractmethod
        def nldsl_dsl(self):
            """How the placeholder should be rendered in NLDSL function, in the grammar section."""
            ...

        @property
        def regex(self):
            return f"(?P<{self.shorthand}>.*)"

        @property
        def regex_repeated(self):
            return f"(?P={self.shorthand})"

        def __repr__(self) -> str:
            return f"<{self.shorthand.upper()}>"


class Singleton(
    _Argument
):  # pylint: disable=too-few-public-methods # it's a dataclass
    class DSL(_Argument.DSL):
        @property
        def is_in_quotes(self) -> bool:
            if not isinstance(self.value, str):
                return False
            if len(self.value) < 2:
                return False
            return (self.value[0] == '"' and self.value[-1] == '"') or (
                self.value[0] == "'" and self.value[-1] == "'"
            )

        @property
        def pure(self) -> str:
            if self.is_in_quotes:
                return self.value[1:-1]
            if self.is_number:
                try:
                    if "." in self.value:
                        return float(self.value)
                    else:
                        return int(self.value)
                except TypeError:
                    pass
            return self.value

        @property
        def is_number(self) -> bool:
            return is_float(self.value)

        def __str__(self) -> str:
            return str(self.value)

        def relaxed_equal(self, other: str | int | float) -> bool:
            if isinstance(other, list):
                return Listleton.DSL(
                    [self], self.index_in_parent
                ).relaxed_equal(other)
            return self.pure == other or self.value == other

    class Placeholder(_Argument.Placeholder):
        base_shorthand = "arg"

        @property
        def nldsl_code(self) -> str:
            return f"{{args['{self.shorthand}']}}"

        @property
        def nldsl_dsl(self):
            return f"${self.shorthand}"


class Choicleton(Singleton):
    class Placeholder(Singleton.Placeholder):
        base_shorthand = "cho"

        def __init__(  # pylint: disable=super-init-not-called # override the abstract method
            self, l_arg: Singleton.DSL, r_arg: Singleton.DSL, id_provider
        ):
            self.examples = [l_arg.value, r_arg.value]
            id_generator = self._id_generator_ref(  # pylint: disable=redefined-outer-name # that's what this generator is for
                id_provider
            )
            self.id = next(id_generator)
            self.choices = [l_arg.pure, r_arg.pure]
            self.linked = False

        def add_choice(self, choice: Singleton.Placeholder):
            self.examples.append(choice.value)
            self.choices.append(choice.pure)

        @property
        def nldsl_code_choice(self) -> str:
            return f"args['{self.shorthand}']"

        @property
        def nldsl_grammar_mod(self) -> str:
            return self.nldsl_dsl[1:] + f" := {{ {', '.join(self.choices)} }}\n"

        @property
        def regex(self):
            return f"({'|'.join(self.choices)})"

        @property
        def regex_repeated(self):
            return self.regex


class Listleton(
    _Argument
):  # pylint: disable=too-few-public-methods # it's a dataclass
    class DSL(_Argument.DSL):
        def __str__(self) -> str:
            return ", ".join([str(x) for x in self.value])

        def relaxed_equal(self, other: list | str) -> bool:
            if isinstance(other, list):
                if len(self.value) != len(other):
                    return False
                match = True
                for i, val in enumerate(self.value):
                    match = match and val.relaxed_equal(other[i])
                return match
            if isinstance(other, str):
                if len(self.value) != 1:
                    return False
                return self.value[0].relaxed_equal(other)
            return False

    class Placeholder(_Argument.Placeholder):
        base_shorthand = "lst"

        def __init__(
            self, id_factory: _IdProvider, examples, placeholding_for: ast.AST
        ):
            super().__init__(id_factory, examples, placeholding_for)
            self.linked_choicleton = None

        def link_choicleton(self, choicleton: Choicleton.Placeholder):
            choicleton.linked = True
            self.linked_choicleton = choicleton

        @property
        def nldsl_code_mod(self):
            result = ""
            if self.linked_choicleton is not None:
                result += f'args["{self.shorthand}"], args["{self.linked_choicleton.shorthand}"] = zip(*args["{self.shorthand}"])\n'
            result += f'args["{self.shorthand}"] = list_to_string(args["{self.shorthand}"])'
            return result

        @property
        def nldsl_code(self) -> str:
            return f"{{args['{self.shorthand}']}}"

        @property
        def nldsl_dsl(self):
            result = f"${self.shorthand}[$i]"
            if self.linked_choicleton is not None:
                result = result[:-1] + f" {self.linked_choicleton.nldsl_dsl}]"
            return result

        def __str__(self) -> str:
            return f"{self.__repr__()}"


class Operaton(_Argument):
    class DSL(_Argument.DSL):
        def __init__(self, lhs, op, rhs, index_in_parent: int):
            self.index_in_parent = index_in_parent
            self.lhs = lhs
            self.op = op
            self.rhs = rhs

        def __str__(self) -> str:
            return f"{self.lhs} {self.op} {self.rhs}"

        def relaxed_equal(self, vals: list) -> bool:
            if not isinstance(vals, list):
                return False
            if len(vals) < 3:
                return False
            lhs = vals[0]
            op = vals[1]
            rhs = vals[2]
            return (
                self.lhs.relaxed_equal(lhs)
                and self.op.relaxed_equal(op)
                and self.rhs.relaxed_equal(rhs)
            )

    class Placeholder(_Argument.Placeholder):
        base_shorthand = "opr"

        @property
        def nldsl_code(self) -> str:
            return f"{{args['{self.shorthand}']}}"

        @property
        def nldsl_dsl(self):
            return f"!{self.shorthand}"


class Pipe(AST):
    base_shorthand = "pipe"

    def __init__(self, placeholding_for: ast.Call | ast.Subscript) -> None:
        self.placeholding_for = placeholding_for

    def __repr__(self) -> str:
        return f"<{self.base_shorthand.upper()}>"

    @property
    def nldsl_code(self) -> str:
        return f"{{{self.base_shorthand}}}"

    @property
    def regex(self):
        return f"(?P<{self.base_shorthand}>.*)"

    @property
    def regex_repeated(self):
        return f"(?P={self.base_shorthand})"
