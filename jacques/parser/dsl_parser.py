from copy import deepcopy
import re
from jacques.jast import *
from jacques.jacques_member import JacquesMember
from ..utils import is_in_quotes, sanitize_from_quotes
from uuid import uuid4 as uuid


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
            jast_in_focus.dsl_string = subquery
            if subquery in self.world_knowledge.COMMON_DSL_TOKENS:
                jast_in_focus.command = subquery
            else:
                for i in range(1, len(subquery)):
                    if subquery[:-i] in self.world_knowledge.COMMON_DSL_TOKENS:
                        jast_in_focus.command = subquery[:-i]
                        self._process_arguments(
                            jast=jast_in_focus, source_string=subquery[-i + 1 :]
                        )
                        break
            if len(query_sequence) > 0:
                jast_in_focus.children = [DslJAST()]
                jast_in_focus = jast_in_focus.children[0]
        return jast

    class ListBuffer:
        def __init__(self) -> None:
            self.buffer = []

        def append(self, obj) -> None:
            self.buffer.append(obj)

        def flush(self) -> List:
            to_return = deepcopy(self.buffer)
            self.buffer = []
            return to_return

    def _process_arguments(
        self, jast: DslJAST, source_string: str
    ) -> List[str | List[str]]:

        matches = re.findall(
            "([\w|\/|.]+|'[\w|\/|,|\s|.]+',|'[\w|\/|,|\s|.]+'|[<>=\-+]+)", source_string
        )

        result = []
        buffer = DslParser.ListBuffer()

        list_is_on = False
        operation_is_on = False

        for each in matches:
            if operation_is_on:
                buffer.append(each)
                result.append(buffer.flush())
                operation_is_on = False
            elif re.match("[><=+\-]+", each):
                buffer.append(result.pop())
                buffer.append(each)
                operation_is_on = True
            elif each[-1] == ",":
                list_is_on = True
                buffer.append(each[:-1])
            elif list_is_on:
                buffer.append(each)
                result.append(buffer.flush())
                list_is_on = False
            else:
                result.append(each)

        # To prepare the dsl string for rule generation, we replace each argument with random hash, and map hashes to arguments
        dictionary = {}
        for each in result:
            h = uuid().hex
            if isinstance(each, list):
                starts_at = jast.dsl_string.find(each[0])
                ends_at = jast.dsl_string.rfind(each[-1]) + len(each[-1])
                jast.dsl_string = (
                    jast.dsl_string[:starts_at] + h + jast.dsl_string[ends_at:]
                )
            else:
                jast.dsl_string = jast.dsl_string.replace(each, h)
            dictionary[h] = each

        result_sanitized_from_quotes = {}
        for k, v in dictionary.items():
            if isinstance(v, list):
                result_sanitized_from_quotes[k] = [sanitize_from_quotes(x) for x in v]
            else:
                result_sanitized_from_quotes[k] = sanitize_from_quotes(v)

        jast.arguments = result_sanitized_from_quotes
