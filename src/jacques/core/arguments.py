from abc import ABC, abstractmethod
from ast import AST
import ast
from typing import Any
from ..utils import id_generator, is_float


class IdProvider:
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

        @abstractmethod
        def relaxed_equal(self, other) -> bool:
            ...

        def __eq__(self, __o: object) -> bool:
            if isinstance(__o, str):
                return self.value == __o
            elif isinstance(__o, _Argument.Placeholder):
                return self.value == __o.examples
            return self.value == __o.value

    class Placeholder(ABC, AST):
        base_shorthand: str

        def _id_generator_ref(self, factory: IdProvider) -> id_generator:
            generator_name = (
                self.__class__.__qualname__.split(".")[0].lower() + "_id_gen"
            )
            return factory.__getattribute__(generator_name)

        def __init__(self, id_factory: IdProvider, examples, placeholding_for: ast.AST):
            id_generator = self._id_generator_ref(id_factory)
            self.id = next(id_generator)
            self.examples = examples
            self.placeholding_for = placeholding_for

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

        @property
        def regex(self):
            return f"(?P<{self.shorthand}>.*)"

        @property
        def regex_repeated(self):
            return f"(?P={self.shorthand})"

        def __repr__(self) -> str:
            return f"<{self.shorthand.upper()}>"


class Singleton(_Argument):
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
                return Listleton.DSL([self], self.index_in_parent).relaxed_equal(other)
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

        def __init__(self, l_arg: Singleton.DSL, r_arg: Singleton.DSL, id_provider):
            self.examples = [l_arg.value, r_arg.value]
            id_generator = self._id_generator_ref(id_provider)
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


class Listleton(_Argument):
    class DSL(_Argument.DSL):
        def __str__(self) -> str:
            return ", ".join([str(x) for x in self.value])

        def relaxed_equal(self, other: list | str) -> bool:
            if isinstance(other, list):
                if len(self.value) != len(other):
                    return False
                match = True
                for i in range(len(self.value)):
                    match = match and self.value[i].relaxed_equal(other[i])
                return match
            elif isinstance(other, str):
                if len(self.value) != 1:
                    return False
                return self.value[0].relaxed_equal(other)
            else:
                return False
                raise NotImplementedError

    class Placeholder(_Argument.Placeholder):
        base_shorthand = "lst"

        def __init__(self, id_factory: IdProvider, examples, placeholding_for: ast.AST):
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
            result += (
                f'args["{self.shorthand}"] = list_to_string(args["{self.shorthand}"])'
            )
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


class Dictleton(Singleton):
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