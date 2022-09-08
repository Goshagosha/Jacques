from copy import deepcopy
import re
from typing import Any, Tuple
from jacques.ast.jacques_ast import *
from jacques.core.arguments import _Argument, Singleton, Listleton, Operaton
from jacques.core.jacques_member import JacquesMember
from uuid import uuid4 as uuid

from jacques.utils import sanitize

COMMAND_NOT_FOUND = "UNKNOWN"


class _ListBuffer:
    def __init__(self) -> None:
        self.buffer = []

    def append(self, obj) -> None:
        item = Singleton.DSL(obj, len(self.buffer))
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

            if len(query_sequence) > 0:
                jast_in_focus.children = [DslJAST()]
                jast_in_focus = jast_in_focus.children[0]
        return jast

    def _deconstruct_dsl_subquery(
        self,
        source_string: str,
    ) -> Tuple[List[str | List[str]], Dict[str, _Argument.DSL | list]]:
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
                l, c, r = buffer.flush()
                result.append(Operaton.DSL(l, c, r, len(result)))
                operation_is_on = False
            elif re.match("[><]+|[><=]\{2\}", each):
                buffer.append(result.pop().value)
                buffer.append(each)
                operation_is_on = True
            elif each.endswith(","):
                list_is_on = True
                buffer.append(each[:-1])
            elif list_is_on:
                buffer.append(each)
                result.append(Listleton.DSL(buffer.flush(), len(result)))
                list_is_on = False
            else:
                result.append(Singleton.DSL(each, len(result)))

        # To prepare the dsl string for rule generation, we replace each argument with a random hash, and map hashes to arguments
        dictionary: Dict[str, _Argument] = {}
        for each in result:
            h = uuid().hex
            if isinstance(each, Listleton.DSL):
                starts_at = each.index_in_parent
                ends_at = len(each.value) + starts_at
                split = split[:starts_at] + [h] + split[ends_at + 1 :]
            elif isinstance(each, Operaton.DSL):
                starts_at = each.index_in_parent
                ends_at = 3 + starts_at
                split = split[:starts_at] + [h] + split[ends_at + 1 :]
            else:
                split[each.index_in_parent] = h
            dictionary[h] = each

        return split, dictionary
