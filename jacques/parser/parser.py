from abc import ABC, abstractmethod
from jacques.j_ast import *


class Parser(ABC):
    def __init__(self, jacques) -> None:
        self.jacques = jacques
        self.world_knowledge = jacques.world_knowledge

    @abstractmethod
    def parse(self, source_string: str) -> JAST:
        ...
