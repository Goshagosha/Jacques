from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import List
import graphviz

from jacques.utils import id_generator


class AstType(Enum):
    CODE = 1
    DSL = 2

class Argument(ABC):
    @abstractmethod
    def __init__(self, value) -> None:
        ...

    def __repr__(self):
        return self.value


class NumberArgument(Argument):
    def __init__(self, value) -> None:
        self.value = str(value)


class StringArgument(Argument):
    def __init__(self, value) -> None:
        self.value = str(value)


class KeywordArgument(Argument):
    def __init__(self, value) -> None:
        self.value = str(value)


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


class JAST:
    def __init__(self, ast_type: AstType) -> None:
        self.type = ast_type
        self.command = None
        self.child = None
        self.arguments: List[Argument] = []

    def compare(self, another_ast: JAST) -> int:
        # produce similarity score
        raise NotImplementedError

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
            name = None
            if isinstance(arg, (ListArgument, OperationArgument)):
                arg_id = arg._plot_to_graph(graph, id_generator)
            else:
                arg_id = next(id_generator)
                graph.node(arg_id, label=str(arg))
            graph.edge(id, arg_id)
        return id
