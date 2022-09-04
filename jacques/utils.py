from typing import Callable, Counter, List
from xmlrpc.client import Boolean
import numpy as np


def is_float(string):
    if isinstance(string, bool):
        return False
    try:
        return float(string) and True
    except ValueError:
        return False


def id_generator():
    num = 0
    while True:
        yield str(num)
        num += 1


def gaussian(x, mu=0, sig=1):
    return np.exp(-np.power(x - mu, 2.0) / (2 * np.power(sig, 2.0)))


def is_in_quotes(string: str) -> bool:
    if len(string) < 2:
        return False
    return (string.startswith("'") and string.endswith("'")) or (
        string.startswith('"') and string.endswith('"')
    )


def sanitize_from_quotes(string: str) -> str:
    return string[1:-1] if is_in_quotes(string) else string


def list_compare(
    list1: List,
    list2: List,
    lambda_left: Callable = None,
    lambda_right: Callable = None,
) -> bool:
    if lambda_left:
        list1 = list(map(lambda_left, list1))
    if lambda_right:
        list2 = list(map(lambda_right, list2))
    return Counter(list1) == Counter(list2)


def key_by_value(dict, value):
    try:
        return list(dict.keys())[list(dict.values()).index(value)]
    except ValueError:
        return None
