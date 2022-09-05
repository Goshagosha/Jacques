from copy import deepcopy
import re
from typing import Any, Tuple
from jacques.ast.jacques_ast import *
from jacques.core.jacques_member import JacquesMember
from uuid import uuid4 as uuid

from jacques.utils import sanitize

COMMAND_NOT_FOUND = "UNKNOWN"


class DslArgument(ABC):
    def __init__(self, value, index_in_parent) -> None:
        self.value = value
        self.index_in_parent = index_in_parent

    @abstractmethod
    def relaxed_equal(self, other: Any) -> bool:
        ...


class DslArgumentSingle(DslArgument):
    def is_in_quotes(self) -> bool:
        if len(self.value) < 2:
            return False
        return (self.value[0] == '"' and self.value[-1] == '"') or (
            self.value[0] == "'" and self.value[-1] == "'"
        )

    def pure(self):
        if self.is_in_quotes():
            return self.value[1:-1]
        else:
            return self.value

    def relaxed_equal(self, other: Any) -> bool:
        if isinstance(other, int):
            other = str(other)
        return self.value == other or self.pure() == other


class DslArgumentList(DslArgument):
    def relaxed_equal(self, other: List) -> bool:
        if not isinstance(other, list):
            raise ValueError("Cannot compare DslArgumentList instance to non-list")
        if len(self.value) != len(other):
            return False
        match = True
        for i in range(len(self.value)):
            match = match and self.value[i].relaxed_equal(other[i])
        return match


class DslArgumentCompare(DslArgument):
    def relaxed_equal(self, other: Any) -> bool:
        if len(other) != 3:
            return False
        return (
            self.left().relaxed_equal(other[0])
            and self.comparator().relaxed_equal(other[1])
            and self.right().relaxed_equal(other[2])
        )

    def left(self):
        return self.value[0]

    def comparator(self):
        return self.value[1]

    def right(self):
        return self.value[2]


class _ListBuffer:
    def __init__(self) -> None:
        self.buffer = []

    def append(self, obj) -> None:
        item = DslArgumentSingle(obj, len(self.buffer))
        self.buffer.append(item)

    def flush(self) -> List:
        to_return = deepcopy(self.buffer)
        self.buffer = []
        return to_return


class DslParser(JacquesMember):
    def parse(self, source_string: str) -> DslJAST:
        source_string = sanitize(source_string)
        jast = DslJAST()
        depth = 0
        jast_in_focus = jast
        query_sequence = source_string.split(" | ")
        while len(query_sequence) > 0:
            jast_in_focus.depth = depth
            depth += 1
            subquery = query_sequence.pop(-1)

            deconstructed, mapping = self._deconstruct_dsl_subquery(subquery)
            jast_in_focus.dsl_string = subquery
            jast_in_focus.deconstructed = deconstructed
            jast_in_focus.mapping = mapping
            jast_in_focus.command = subquery.split(" ")[0]

            if len(query_sequence) > 0:
                jast_in_focus.children = [DslJAST()]
                jast_in_focus = jast_in_focus.children[0]
        return jast

    def _deconstruct_dsl_subquery(
        self,
        source_string: str,
    ) -> Tuple[List[str | List[str]], Dict[str, DslArgument | list]]:
        source_string = sanitize(source_string)
        split = re.findall(
            "([\w|\/|.]+|'[\w|\/|,|\s|.]+',|'[\w|\/|,|\s|.]+'|[<>=\-+]+)", source_string
        )

        result = []
        buffer = _ListBuffer()

        list_is_on = False
        operation_is_on = False

        for each in split:
            if operation_is_on:
                buffer.append(each)
                result.append(DslArgumentCompare(buffer.flush(), len(result)))
                operation_is_on = False
            elif re.match("[><+\-]+|[><=+\-]\{2\}", each):
                buffer.append(result.pop().value)
                buffer.append(each)
                operation_is_on = True
            elif each.endswith(","):
                list_is_on = True
                buffer.append(each[:-1])
            elif list_is_on:
                buffer.append(each)
                result.append(DslArgumentList(buffer.flush(), len(result)))
                list_is_on = False
            else:
                result.append(DslArgumentSingle(each, len(result)))

        # To prepare the dsl string for rule generation, we replace each argument with a random hash, and map hashes to arguments
        dictionary: Dict[str, DslArgument] = {}
        for each in result:
            h = uuid().hex
            if isinstance(each, DslArgumentList):
                starts_at = each.index_in_parent
                ends_at = len(each.value) + starts_at
                split = split[:starts_at] + [h] + split[ends_at + 1 :]
            elif isinstance(each, DslArgumentCompare):
                starts_at = each.index_in_parent
                ends_at = 3 + starts_at
                split = split[:starts_at] + [h] + split[ends_at + 1 :]
            else:
                split[each.index_in_parent] = h
            dictionary[h] = each

        return split, dictionary
