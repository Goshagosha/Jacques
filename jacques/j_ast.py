from __future__ import annotations
from abc import ABC, abstractmethod
import copy
from typing import List
import graphviz

from jacques.utils import id_generator


class Visualizeable(ABC):
    id_generator = id_generator()

    @abstractmethod
    def _visualize_recursive(self, graph) -> str:
        ...


class VisualizeableLeaf(Visualizeable):
    def _visualize_recursive(self, graph) -> str:
        id = next(self.id_generator)
        graph.node(id, str(self))
        return id


class VisualizeableTree(Visualizeable):
    def _visualize_recursive(self, graph) -> str:
        id = next(self.id_generator)
        name = str(type(self).__name__)
        graph.node(id, label=name)
        for each in self.value:
            graph.edge(id, each._visualize_recursive(graph))
        return id


class Argument(ABC):
    @abstractmethod
    def __init__(self, value) -> None:
        ...

    def __repr__(self):
        return self.value

    def __str__(self):
        return str(self.value)


class NumberArgument(Argument, VisualizeableLeaf):
    def __init__(self, value) -> None:
        self.value = value


class StringArgument(Argument, VisualizeableLeaf):
    def __init__(self, value) -> None:
        self.value = str(value)


class KeywordArgument(Argument, VisualizeableLeaf):
    def __init__(self, value) -> None:
        self.value = value


class ListArgument(Argument, VisualizeableTree):
    def __init__(self, value: List[Argument]) -> None:
        self.value = value

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


class ExpressionArgument(Argument, VisualizeableTree):
    def __init__(self, left, op, right) -> None:
        self.value = (left, StringArgument(op), right)


class OperationArgument(Argument, VisualizeableTree):
    def __init__(self, left: Argument, operator: str, right: Argument) -> None:
        self.value = (left, StringArgument(operator), right)

    def __repr__(self):
        return str(list(self.value))


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


class JAST(Visualizeable):
    def __init__(self) -> None:
        self.command = None
        self.children = []
        self.parent = None
        self.arguments: List[Argument] = []

    def set_parent(self, parent: JAST):
        self.parent = parent
        parent.children.append(self)

    def add_child(self, child: JAST):
        self.children.append(child)
        child.parent = self

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
        self._visualize_recursive(graph)
        graph.render()

    def _visualize_recursive(self, graph) -> str:
        id = next(self.id_generator)
        graph.node(id, label=self.command, shape="diamond")
        for child in self.children:
            child_id = child._visualize_recursive(graph)
            graph.edge(id, child_id)
        for arg in self.arguments:
            arg_id = arg._visualize_recursive(graph)
            graph.edge(id, arg_id)
        return id

    def __contains__(self, other_ast):
        other_command = other_ast.command
        if self.command == other_command:
            return True
        for child in self.children:
            if other_ast in child:
                return True
        return False

    def __sub__(self, other_ast):
        j = copy.deepcopy(self)
        raise NotImplementedError


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
