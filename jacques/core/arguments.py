from abc import ABC, abstractmethod, abstractproperty
from ast import AST
import ast
import re
from typing import Any, List
from jacques.utils import id_generator


class IdFactory:
    def __init__(self) -> None:
        self.singleton_id_gen = id_generator()
        self.listleton_id_gen = id_generator()
        self.operaton_id_gen = id_generator()


class _Argument(ABC):
    class DSL(ABC):
        def __init__(self, value: Any, index_in_parent: int):
            self.value = value
            self.index_in_parent = index_in_parent

        @abstractmethod
        def relaxed_equal(self, other: Any) -> bool:
            ...

        @abstractmethod
        def __str__(self) -> str:
            ...

    class Code(ABC):
        def __init__(self, path: List[str], value: Any):
            self.path = path
            self.value = value

        @abstractmethod
        def create_placeholder(self, id_generator: id_generator) -> Any:
            ...

    class Placeholder(ABC, AST):
        base_shorthand: str

        def _id_generator_ref(self, factory: IdFactory) -> id_generator:
            generator_name = (
                self.__class__.__qualname__.split(".")[0].lower() + "_id_gen"
            )
            return factory.__getattribute__(generator_name)

        def __init__(self, id_factory: IdFactory, examples):
            id_generator = self._id_generator_ref(id_factory)
            self.id = next(id_generator)
            self.examples = examples

        @property
        def shorthand(self):
            return self.base_shorthand + str(self.id)

        @property
        @abstractmethod
        def nldsl_code(self) -> str:
            ...

        @property
        @abstractmethod
        def nldsl_dsl(self):
            ...

        def __repr__(self) -> str:
            return f"<{self.shorthand.upper()}>"


class Singleton(_Argument):
    class DSL(_Argument.DSL):
        @property
        def is_in_quotes(self) -> bool:
            if len(self.value) < 2:
                return False
            return (self.value[0] == '"' and self.value[-1] == '"') or (
                self.value[0] == "'" and self.value[-1] == "'"
            )

        @property
        def pure(self) -> str:
            if self.is_in_quotes:
                return self.value[1:-1]
            return self.value

        def relaxed_equal(self, other) -> bool:
            if isinstance(other, Listleton.Code):
                return [self.value] == other.value or [self.pure] == other.value
            elif isinstance(other, Singleton.Code):
                return self.value == other.value or self.pure == other.value
            elif isinstance(other, str):
                return self.value == other or self.pure == other
            else:
                return False

        def __str__(self) -> str:
            return str(self.value)

    class Code(_Argument.Code):
        def create_placeholder(self, id_generator: id_generator) -> Any:
            return Singleton.Placeholder(id_generator, self.value)

    class Placeholder(_Argument.Placeholder):
        base_shorthand = "arg"

        @property
        def nldsl_code(self) -> str:
            return f"{{args['{self.shorthand}']}}"

        @property
        def nldsl_dsl(self):
            return f"${self.shorthand}"


class Listleton(_Argument):
    class DSL(_Argument.DSL):
        def relaxed_equal(self, other) -> bool:
            if not isinstance(other, Listleton.Code):
                return False
            if len(self.value) != len(other.value):
                return False
            match = True
            for i in range(len(self.value)):
                match = match and self.value[i].relaxed_equal(other.value[i])
            return match

        def __str__(self) -> str:
            return " ,".join([str(x) for x in self.value])

    class Code(_Argument.Code):
        def create_placeholder(self, id_generator: id_generator) -> Any:
            return Listleton.Placeholder(id_generator, self.value)

    class Placeholder(_Argument.Placeholder):
        base_shorthand = "lst"

        @property
        def nldsl_code(self) -> str:
            return f"{{args['{self.shorthand}']}}"

        @property
        def nldsl_dsl(self):
            return f"${self.shorthand}[$i]"

        def __str__(self) -> str:
            return f"{self.__repr__()}"


class Operaton(_Argument):
    class DSL(_Argument.DSL):
        def __init__(self, lhs, op, rhs, index_in_parent: int):
            self.index_in_parent = index_in_parent
            self.lhs = lhs
            self.op = op
            self.rhs = rhs

        def relaxed_equal(self, other) -> bool:
            if not isinstance(other, Operaton.Code):
                return False
            return (
                self.lhs.relaxed_equal(other.lhs)
                and self.op.relaxed_equal(other.op)
                and self.rhs.relaxed_equal(other.rhs)
            )

        def __str__(self) -> str:
            return f"{self.lhs} {self.op} {self.rhs}"

    class Placeholder(_Argument.Placeholder):
        base_shorthand = "opr"

        @property
        def nldsl_code(self) -> str:
            return f"{{args['{self.shorthand}']}}"

        @property
        def nldsl_dsl(self):
            return f"!{self.shorthand}"

    class Code(_Argument.Code):
        def __init__(self, path: List[str], lhs, op, rhs):
            self.path = path
            self.lhs = lhs
            self.op = op
            self.rhs = rhs

        def create_placeholder(self, id_generator: id_generator) -> Any:
            return Operaton.Placeholder(id_generator, self.value)

        @property
        def value(self) -> str:
            return f"{self.lhs} {self.op} {self.rhs}"


class Pipe(AST):
    base_shorthand = "pipe"

    def __init__(self, placeholding_for: ast.Call | ast.Subscript) -> None:
        self.placeholding_for = placeholding_for

    def __repr__(self) -> str:
        return f"<{self.base_shorthand.upper()}>"

    @property
    def nldsl_code(self) -> str:
        return f"{{{self.base_shorthand}}}"
