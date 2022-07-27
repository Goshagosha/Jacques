from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import List
import graphviz

from jacques.utils import id_generator


class Argument(ABC):
    @abstractmethod
    def __init__(self, value) -> None:
        ...

    def __repr__(self):
        return self.value


class NumberArgument(Argument):
    def __init__(self, value) -> None:
        self.value = value


class StringArgument(Argument):
    def __init__(self, value) -> None:
        self.value = value


class KeywordArgument(Argument):
    def __init__(self, value) -> None:
        self.value = value


class ListArgument(Argument):
    def __init__(self, value: List[Argument]) -> None:
        self.value = value

    def _plot_to_graph(self, graph, id_generator) -> str:
        id = next(id_generator)
        name = str(type(self))
        graph.node(id, label=name)
        for each in self.value:
            each_id = next(id_generator)
            graph.node(each_id, str(each))
            graph.edge(id, each_id)
        return id

    def __iter__(self):
        return ListArgumentIterator(self)


class ListArgumentIterator:
    def __init__(self, list_argument: ListArgument) -> None:
        self.idx = 0
        self.list = list_argument.value

    def __iter__(self):
        return self

    def __next__(self):
        self.idx += 1
        try:
            return self.list[self.idx - 1]
        except IndexError:
            self.idx = 0
            raise StopIteration


class OperationArgument(Argument):
    def __init__(self, left: Argument, operator: str, right: Argument) -> None:
        self.value = (left, operator, right)

    def __repr__(self):
        return str(list(self.value))

    def _plot_to_graph(self, graph, id_generator) -> str:
        id = next(id_generator)
        name = str(type(self))
        graph.node(id, label=name)
        for each in self.value:
            each_id = next(id_generator)
            graph.node(each_id, str(each))
            graph.edge(id, each_id)
        return id


def flatten_argument_set(_list: List[Argument]):
    result = []
    for arg in _list:
        if isinstance(arg, ListArgument):
            result += flatten_argument_set(arg)
        elif isinstance(arg, OperationArgument):
            result += ["operation_argument"]
        else:
            result += [arg]
    return result


class JAST:
    def __init__(self) -> None:
        self.command = None
        self.child = None
        self.arguments: List[Argument] = []

    def compare(self, another_ast: JAST) -> int:
        score = 0
        # hacky solution
        this_buffer_of_args = flatten_argument_set(self.arguments.copy())
        other_buffer_of_args = flatten_argument_set(another_ast.arguments.copy())
        if len(this_buffer_of_args) == 0 and len(other_buffer_of_args) == 0:
            score += 1
        for each in this_buffer_of_args:
            for every in other_buffer_of_args:
                score += int(each == every)

        return score

    def visualize(self, export_name) -> None:
        graph = graphviz.Graph(name=export_name, format="png")
        id_gen = id_generator()
        self._visualize_recursive(graph, id_gen)
        graph.render()

    def _visualize_recursive(self, graph, id_generator) -> str:
        id = next(id_generator)
        graph.node(id, label=self.command, shape="diamond")
        if self.child:
            child_id = self.child._visualize_recursive(graph, id_generator)
            graph.edge(id, child_id)
        for arg in self.arguments:
            if isinstance(arg, (ListArgument, OperationArgument)):
                arg_id = arg._plot_to_graph(graph, id_generator)
            else:
                arg_id = next(id_generator)
                graph.node(arg_id, label=str(arg))
            graph.edge(id, arg_id)
        return id


class CodeJAST(JAST):
    def __init__(self):
        self.code_ast = None
        super().__init__()


class DslJAST(JAST):
    def __init__(self):
        self.dsl_string = None
        super().__init__()


class JastFamily:
    def __init__(self, from_jast: JAST):
        self.command = from_jast.command
        self.samples = [from_jast]

    def append_sample(self, sample: JAST):
        if sample.command != self.command:
            raise Exception(
                "JAST sample you are trying to add to a family starts with a different command"
            )
        self.samples.append(sample)
