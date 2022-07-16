import re
from typing import List
from jacques.j_ast import *
from jacques.parser.parser import Parser
from jacques.utils import is_float


class DslParser(Parser):
    def parse(self, source_string: str) -> JAST:
        jast = JAST(AstType.DSL)
        jast_in_focus = jast
        query_sequence = source_string.split(" | ")
        while len(query_sequence) > 0:
            subquery = query_sequence.pop(-1)
            if subquery in self.world_knowledge.COMMON_DSL_TOKENS:
                jast_in_focus.command = subquery
            else:
                for i in range(1, len(subquery)):
                    if subquery[:-i] in self.world_knowledge.COMMON_DSL_TOKENS:
                        jast_in_focus.command = subquery[:-i]
                        jast_in_focus.arguments = self._process_arguments_string(
                            subquery[-i + 1 :]
                        )
                        break
            if len(query_sequence) > 0:
                jast_in_focus.child = JAST(AstType.DSL)
                jast_in_focus = jast_in_focus.child
        return jast

    def _process_arguments_string(self, source_string: str) -> List:
        matches = re.findall(
            "([\w|\/]+|'[\w|\/|,|\s]+',|'[\w|\/|,|\s]+'|[<>=\-+]+)", source_string
        )
        result: List[Argument] = []
        _list_buffer = []
        _operation_buffer = []
        for each in matches:
            # flush operation buffer if we already started filling it
            if len(_operation_buffer) == 2:
                resolved = self._resolve_non_list_type(each)
                _operation_buffer.append(resolved)
                result.append(
                    OperationArgument(
                        _operation_buffer[0], _operation_buffer[1], _operation_buffer[2]
                    )
                )
                _operation_buffer = []
            # if the word is an operation, its neighbours are concatted into an operation
            elif re.match("[><=+\-]+", each):
                _operation_buffer = [result.pop(-1), StringArgument(each)]
            # if the word ends in comma, its concat with the next into a list
            elif each[-1] == ",":
                resolved = self._resolve_non_list_type(each[:-1])
                _list_buffer.append(resolved)
            # otherwise flush buffer if it's not empty:
            elif len(_list_buffer) > 0:
                resolved = self._resolve_non_list_type(each)
                _list_buffer.append(resolved)
                result.append(ListArgument(_list_buffer))
                _list_buffer = []
            else:
                result.append(self._resolve_non_list_type(each))
        return result

    def _resolve_non_list_type(self, string: str):
        if string.startswith("'") or string.startswith('"'):
            return StringArgument(string)
        if is_float(string):
            return NumberArgument(string)
        if (
            string in self.problem_knowledge.encountered_object_names
            or string in self.problem_knowledge.encountered_variables
        ):
            return KeywordArgument(string)
        # otherwise we append the keyword, there might be some logic to exploit here
        self.problem_knowledge.encountered_object_names.append(string)
        return KeywordArgument(string)
