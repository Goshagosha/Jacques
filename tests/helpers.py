from pathlib import Path

import jacques.world_knowledge as wk
from main import Jacques


def pp(string):
    j = Jacques(wk)
    return j.python_parser.parse(string)


def draw_test_result(tree, name):
    save_path = "tests/test_output"
    Path(save_path).mkdir(exist_ok=True)
    tree.visualize(f"{save_path}/{name}")
