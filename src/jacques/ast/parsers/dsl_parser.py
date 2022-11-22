from copy import deepcopy
from typing import List
import re
from ..jacques_ast import DslJAST
from ...core.arguments import _Argument, Singleton, Listleton, Operaton
from ...core.jacques_member import JacquesMember

from ...utils import sanitize

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


class DslParser(JacquesMember): # pylint: disable=too-few-public-methods
    def parse(self, source_string: str) -> DslJAST:
        source_string = sanitize(source_string)
        jast = DslJAST()
        depth = 0
        jast_in_focus = jast
        query_sequence = source_string.split(" | ")
        if " = " in query_sequence[0]:
            split = query_sequence[0].split(" = ")
            query_sequence[0] = split[1]
            self.jacques.encountered(split[0])
        while len(query_sequence) > 0:
            jast_in_focus.depth = depth
            depth += 1
            subquery = query_sequence.pop(-1)

            deconstructed = self._deconstruct_dsl_subquery(subquery)
            jast_in_focus.dsl_string = subquery
            jast_in_focus.deconstructed = deconstructed

            if len(query_sequence) > 0:
                jast_in_focus.children = [DslJAST()]
                jast_in_focus = jast_in_focus.children[0]
        return jast

    def _deconstruct_dsl_subquery(
        self,
        source_string: str,
    ) -> List[_Argument.DSL | list]:
        source_string = sanitize(source_string)
        split = re.findall(
            r"([\w|/|.]+|'[\w|/|,|\s|.]+',|'[\w|/|,|\s|.]+'|[<>=\-+]+)", source_string
        )

        result = []
        buffer = _ListBuffer()

        list_is_on = False
        operation_is_on = False

        for each in split:
            if operation_is_on:
                buffer.append(each)
                l, c, r = buffer.flush() # pylint: disable=invalid-name
                result.append(Operaton.DSL(l, c, r, len(result)))
                operation_is_on = False
            elif re.match(r"[+-/*%]|[><]|[><=]{2}", each):
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

        for each in result:
            if isinstance(each, Listleton.DSL):
                starts_at = each.index_in_parent
                ends_at = len(each.value) + starts_at
                split = split[:starts_at] + [each] + split[ends_at + 1 :]
            elif isinstance(each, Operaton.DSL):
                starts_at = each.index_in_parent
                ends_at = 3 + starts_at
                split = split[:starts_at] + [each] + split[ends_at:]
            else:
                if len(split) > each.index_in_parent:
                    split[each.index_in_parent] = each
                else:
                    split.append(each)

        return split
