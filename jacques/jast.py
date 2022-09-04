from __future__ import annotations
from abc import ABC, abstractmethod
from ast import AST
import copy
from platform import java_ver
from typing import Dict, List, Tuple
import graphviz
from jacques.python_ast_utils import Lst, Arg

from jacques.utils import id_generator


class Visualizeable(ABC):
    id_generator = id_generator()

    @abstractmethod
    def _visualize_recursive(self, graph) -> str:
        ...


class VisualizeableLeaf(Visualizeable):
    def _visualize_recursive(self, graph) -> str:
        id = next(self.id_generator)
        name = f"{type(self).__name__}\n{str(self)}"
        graph.node(id, label=name)
        return id


class VisualizeableTree(Visualizeable):
    def _visualize_recursive(self, graph) -> str:
        id = next(self.id_generator)
        name = str(type(self).__name__)
        graph.node(id, label=name)
        for each in self.value:
            graph.edge(id, each._visualize_recursive(graph))
        return id


class JAST(Visualizeable):
    def __init__(self) -> None:
        self.command: str = None
        self.children: List[JAST] = []
        self.depth: int = None
        self.inverse_depth: int = None
        self.parent: JAST = None
        self.arguments: Dict = {}

    def set_parent(self, parent: JAST):
        self.parent = parent
        parent.children.append(self)

    def add_child(self, child: JAST):
        self.children.append(child)
        child.parent = self

    def inverse_depth_rec(self):
        if len(self.children) == 0:
            self.inverse_depth = 0
        else:
            max_in_child = 0
            for child in self.children:
                child_d = child.inverse_depth_rec()
                max_in_child = max(max_in_child, child_d)
            self.inverse_depth = max_in_child + 1
        return self.inverse_depth

    def visualize(self, export_name) -> None:
        graph = graphviz.Graph(name=export_name, format="png")
        self._visualize_recursive(graph)
        graph.render()

    def _visualize_recursive(self, graph) -> str:
        id = next(self.id_generator)
        label = f"depth:{self.depth}; inv.depth:{self.inverse_depth}\n{self.command}"
        graph.node(id, label=label, shape="diamond")
        for child in self.children:
            child_id = child._visualize_recursive(graph)
            graph.edge(id, child_id)
        for argument, path in self.arguments.items():
            arg_id = next(self.id_generator)
            label = f"{path}\n{argument}"
            graph.node(arg_id, label=label)
            graph.edge(id, arg_id)
        return id

    def __contains__(self, other_ast) -> bool:
        other_command = other_ast.command
        if self.command == other_command:
            return True
        for child in self.children:
            if other_ast in child:
                return True
        return False

    def __sub__(self, other_ast) -> JAST:
        j = copy.deepcopy(self)
        raise NotImplementedError

    def __iter__(self):
        """Recursive iterator

        Yields:
            _type_: _description_
        """
        yield self
        for child in self.children:
            for node in child:
                yield node


class CodeJAST(JAST):
    def __init__(self):
        self.code_ast: AST = None
        super().__init__()

    def childfree_copy(self) -> CodeJAST:
        new = CodeJAST()
        new.command = self.command
        new.depth = self.depth
        new.inverse_depth = self.inverse_depth
        new.code_ast = self.code_ast
        return new


class DslJAST(JAST):
    def __init__(self):
        self.dsl_string: str = None
        self.deconstructed: list = None
        self.mapping: Dict = None
        super().__init__()

    def reconstruct(self):
        result = []
        for h in self.deconstructed:
            arg = self.mapping[h]
            if isinstance(arg, list):
                result.append(", ".join([m.value for m in arg]))
            else:
                if isinstance(arg, (Lst, Arg)):
                    result.append(str(arg))
                else:
                    result.append(arg.value)
        return " ".join(result)