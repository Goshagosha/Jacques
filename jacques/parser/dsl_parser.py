import re
from jacques.j_ast import *
from jacques.parser.parser import Parser


class DslParser(Parser):
    def parse(self, source_string: str, dump_entry_point=True) -> DslJAST:
        jast = DslJAST()
        depth = 0
        jast_in_focus = jast
        query_sequence = source_string.split(" | ")
        if dump_entry_point:
            query_sequence = query_sequence[1:]
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
                        jast_in_focus.arguments = self._process_arguments(
                            subquery[-i + 1 :]
                        )
                        break
            if len(query_sequence) > 0:
                jast_in_focus.children = [DslJAST()]
                jast_in_focus = jast_in_focus.children[0]
        return jast

    def _process_arguments(self, source_string: str) -> Dict[str, int]:
        matches = re.findall(
            "([\w|\/]+|'[\w|\/|,|\s]+',|'[\w|\/|,|\s]+'|[<>=\-+]+)", source_string
        )
        result = {}

        group_tag = 0
        list_is_on = False
        operation_is_on = False

        for each in matches:
            if operation_is_on:
                result[each] = group_tag
                operation_is_on = False
                group_tag += 1
            elif re.match("[><=+\-]+", each):
                group_tag -= 1
                result[each] = group_tag
                operation_is_on = True
            elif each[-1] == ",":
                if list_is_on:
                    result[each] = group_tag
                else:
                    list_is_on = True
            elif list_is_on:
                result[each] = group_tag
                list_is_on = False
                group_tag += 1
            else:
                result[each] = group_tag
                group_tag += 1
        return result
