from abc import ABC, abstractmethod
from jacques.j_ast import *
from jacques.problem_knowledge import ProblemKnowledge


class Parser(ABC):
    def __init__(self, world_knowledge, problem_knowledge: ProblemKnowledge) -> None:
        self.world_knowledge = world_knowledge
        self.problem_knowledge = problem_knowledge

    @abstractmethod
    def parse(self, source_string: str) -> JAST:
        ...
