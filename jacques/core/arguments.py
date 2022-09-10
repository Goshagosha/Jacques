from abc import ABC, abstractmethod, abstractproperty
from ast import AST
import ast
from calendar import c
from tokenize import Single
from typing import Any, List, Tuple
from jacques.utils import id_generator


class IdProvider:
    def __init__(self) -> None:
        pass
        # self.singleton_id_gen = id_generator()
        # self.listleton_id_gen = id_generator()
        # self.operaton_id_gen = id_generator()
        # self.choicleton_id_gen = id_generator()

    def __getattribute__(self, __name: str) -> Any:
        if __name.endswith("_id_gen"):
            try:
                return super().__getattribute__(__name)
            except AttributeError:
                self.__setattr__(__name, id_generator())
                return super().__getattribute__(__name)
        else:
            return super().__getattribute__(__name)


class ListIndex:
    def __init__(self, index):
        self.index = index


class _Argument(ABC):
    class DSL(ABC):
        def __init__(self, value: Any, index_in_parent: int):
            self.value = value
            self.index_in_parent = index_in_parent

        @abstractmethod
        def __str__(self) -> str:
            ...

    class Code(ABC):
        def __init__(self, path: List[str], value: Any):
            self.path = path
            self.value = value

        @abstractmethod
        def relaxed_equal(self, other: Any) -> bool:
            ...

        @abstractmethod
        def create_placeholder(
            self, id_generator: id_generator, matched_DSL: Any
        ) -> Any:
            ...

    class Placeholder(ABC, AST):
        base_shorthand: str

        def _id_generator_ref(self, factory: IdProvider) -> id_generator:
            generator_name = (
                self.__class__.__qualname__.split(".")[0].lower() + "_id_gen"
            )
            return factory.__getattribute__(generator_name)

        def __init__(self, id_factory: IdProvider, examples):
            id_generator = self._id_generator_ref(id_factory)
            self.id = next(id_generator)
            self.examples = examples

        @property
        def shorthand(self):
            return self.base_shorthand + str(self.id)

        @property
        def nldsl_grammar_mod(self):
            ...

        @property
        def nldsl_code_mod(self):
            ...

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

        def __str__(self) -> str:
            return str(self.value)

    class Code(_Argument.Code):
        def relaxed_equal(self, other) -> bool:
            if isinstance(other, Singleton.DSL):
                value = str(self.value)
                return value == other.value or value == other.pure
            return False

        def create_placeholder(self, id_generator: id_generator, matched_DSL) -> Any:
            # Hacky:
            # if not matched_DSL.is_in_quotes:
            #     return Choicleton.Placeholder(id_generator, self.value, matched_DSL)
            return Singleton.Placeholder(id_generator, self.value)

    class Placeholder(_Argument.Placeholder):
        base_shorthand = "arg"

        @property
        def nldsl_code(self) -> str:
            return f"{{args['{self.shorthand}']}}"

        @property
        def nldsl_dsl(self):
            return f"${self.shorthand}"


class Choicleton(Singleton):
    class DSL(Singleton.DSL):
        ...

    class Code(Singleton.Code):
        ...

    class Placeholder(Singleton.Placeholder):
        base_shorthand = "cho"

        def __init__(self, id_factory: IdProvider, examples, matched_DSL):
            super().__init__(id_factory, examples)
            self.choices = [matched_DSL.pure]

        @property
        def nldsl_grammar_mod(self) -> str:
            return self.nldsl_dsl + f"{{{', '.join(self.choices)}}}\n"


class Listleton(_Argument):
    class DSL(_Argument.DSL):
        def __str__(self) -> str:
            return " ,".join([str(x) for x in self.value])

    class Code(_Argument.Code):
        def __init__(self, path: List[str], value: Any):
            super().__init__(path, value)

        def relaxed_equal(self, other) -> bool:
            if not isinstance(other, (Listleton.DSL, Singleton.DSL)):
                return False
            if isinstance(other, Singleton.DSL):
                return self.value[0].relaxed_equal(other)
            if isinstance(other, Listleton.DSL):
                if len(self.value) != len(other.value):
                    return False

                match = True
                for i in range(len(self.value)):
                    match = match and self.value[i].relaxed_equal(other.value[i])
                return match

        def create_placeholder(self, id_generator: id_generator, matched_DSL) -> Any:
            return Listleton.Placeholder(id_generator, self.value)

    class Placeholder(_Argument.Placeholder):
        base_shorthand = "lst"

        @property
        def nldsl_code_mod(self):
            return (
                f'args["{self.shorthand}"] = list_to_string(args["{self.shorthand}"])'
            )

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

        def __str__(self) -> str:
            return f"{self.lhs} {self.op} {self.rhs}"

    class Code(_Argument.Code):
        def __init__(self, path: List[str], lhs, op, rhs):
            self.path = path
            self.lhs = Singleton.Code([], lhs)
            self.op = Singleton.Code([], op)
            self.rhs = Singleton.Code([], rhs)

        def relaxed_equal(self, other) -> bool:
            if not isinstance(other, Operaton.DSL):
                return False
            return (
                self.lhs.relaxed_equal(other.lhs)
                and self.op.relaxed_equal(other.op)
                and self.rhs.relaxed_equal(other.rhs)
            )

        def create_placeholder(self, id_generator: id_generator, matched_DSL) -> Any:
            return Operaton.Placeholder(id_generator, self.value)

        @property
        def value(self) -> str:
            return f"{self.lhs} {self.op} {self.rhs}"

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


class Dictleton(Singleton):
    class Code(Singleton.Code):
        def __init__(self, path: List[str], value: dict):
            if len(value) > 1:
                raise ValueError("Dictleton can only contain one key-value pair")
            value = [
                Singleton.Code([], list(value.keys())[0]),
                Singleton.Code([], list(value.values())[0]),
            ]
            super().__init__(path, value)

        def relaxed_equal(self, other: Singleton.DSL) -> bool:
            return self.lhs.relaxed_equal(other) or self.rhs.relaxed_equal(other)

        def get_placeholder(self, id_generator: id_generator) -> Any:
            try:
                return self._placeholder
            except AttributeError:
                self._placeholder = self.create_placeholder(id_generator)
                return self._placeholder

        @property
        def lhs(self) -> str:
            return self.value[0]

        @lhs.setter
        def lhs(self, value: Singleton.Code):
            self.value[0] = value

        @property
        def rhs(self) -> str:
            return self.value[1]

        @rhs.setter
        def rhs(self, value: Singleton.Code):
            self.value[1] = value

        def create_placeholder(
            self,
            id_generator: id_generator,
        ) -> Any:
            placeholder = Dictleton.Placeholder(id_generator, self.value)
            placeholder.value = self.value.copy()
            return placeholder

    class Placeholder(Singleton.Placeholder):
        base_shorthand = "dct"

        def __init__(
            self,
            id_factory: IdProvider,
            examples,
        ):
            self.value = []
            super().__init__(id_factory, examples)

        @property
        def lhs(self) -> str:
            return self.value[0]

        @lhs.setter
        def lhs(self, value: Singleton.Placeholder):
            self.value[0] = value

        @property
        def rhs(self) -> str:
            return self.value[1]

        @rhs.setter
        def rhs(self, value: Singleton.Placeholder):
            self.value[1] = value

        @property
        def nldsl_dsl(self):
            raise NotImplementedError("Dictleton does not have a DSL implementation")

        @property
        def nldsl_code_mod(self):
            if isinstance(self.lhs, Singleton.Code):
                lhs = f"{self.lhs.value}"
            else:
                lhs = f"args['{self.lhs.shorthand}']"
            if isinstance(self.rhs, Singleton.Code):
                rhs = f"{self.rhs.value}"
            else:
                rhs = f"args['{self.rhs.shorthand}']"
            return f'args["{self.shorthand}"] = {{{lhs} : {rhs}}}'
