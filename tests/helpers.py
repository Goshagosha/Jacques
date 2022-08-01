from pathlib import Path
from jacques.parser.python_parser import PythonParser

import jacques.world_knowledge as wk


def pp(string):
    return PythonParser(world_knowledge=wk, problem_knowledge=None).parse(string)


def draw_test_result(tree, name):
    save_path = "tests/test_output"
    Path(save_path).mkdir(exist_ok=True)
    tree.visualize(f"{save_path}/{name}")
