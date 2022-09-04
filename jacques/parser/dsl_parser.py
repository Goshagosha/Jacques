from copy import deepcopy
import re
from typing import Any
from jacques.ast.jacques_ast import *
from jacques.core.jacques_member import JacquesMember
from uuid import uuid4 as uuid

COMMAND_NOT_FOUND = "UNKNOWN"


class DslArgument:
    def __init__(self, value, index_in_parent) -> None:
        self.value = value
        self.index_in_parent = index_in_parent

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
        return self.value == other or self.pure() == other


class _ListBuffer:
    def __init__(self) -> None:
        self.buffer = []

    def append(self, obj) -> None:
        self.buffer.append(obj)

    def flush(self) -> List:
        to_return = deepcopy(self.buffer)
        self.buffer = []
        return to_return


class DslParser(JacquesMember):
    def parse(self, source_string: str) -> DslJAST:
        try:
            if source_string[-1:] == "\n":
                source_string = source_string[:-1]
        except IndexError:
            pass
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
        try:
            if source_string[0] == " ":
                source_string = source_string[1:]
            if source_string[-1] == " ":
                source_string = source_string[:-1]
        except IndexError:
            pass
        split = re.findall(
            "([\w|\/|.]+|'[\w|\/|,|\s|.]+',|'[\w|\/|,|\s|.]+'|[<>=\-+]+)", source_string
        )

        result = []
        buffer = _ListBuffer()

        list_is_on = False
        operation_is_on = False

        for i, each in enumerate(split):
            each = DslArgument(each, i)
            if operation_is_on:
                buffer.append(each)
                result.append(buffer.flush())
                operation_is_on = False
            elif re.match("[><+\-]+|[><=+\-]\{2\}", each.value):
                buffer.append(result.pop())
                buffer.append(each)
                operation_is_on = True
            elif each.value[-1] == ",":
                list_is_on = True
                each.value = each.value[:-1]
                buffer.append(each)
            elif list_is_on:
                buffer.append(each)
                result.append(buffer.flush())
                list_is_on = False
            else:
                result.append(each)

        # To prepare the dsl string for rule generation, we replace each argument with a random hash, and map hashes to arguments
        dictionary: Dict[str, DslArgument] = {}
        for each in result:
            h = uuid().hex
            if isinstance(each, list):
                starts_at = each[0].index_in_parent
                ends_at = each[-1].index_in_parent
                split = split[:starts_at] + [h] + split[ends_at + 1 :]
            else:
                split[each.index_in_parent] = h
            dictionary[h] = each

        return split, dictionary
