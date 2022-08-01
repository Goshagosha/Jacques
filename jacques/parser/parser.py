from abc import ABC, abstractmethod
from jacques.j_ast import *
from jacques.problem_knowledge import ProblemKnowledge


class Parser(ABC):
    def __init__(self, jacques) -> None:
        self.world_knowledge = jacques.world_knowledge
        self.problem_knowledge = jacques.problem_knowledge

    @abstractmethod
    def parse(self, source_string: str) -> JAST:
        ...
