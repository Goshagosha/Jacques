"""This module provides reuseable utilities for many of the other modules in the jacques package."""
from typing import Callable, Counter, List
import numpy as np


def is_float(string) -> bool:
    if isinstance(string, bool):
        return False
    try:
        _ = float(string)
        return True
    except ValueError:
        return False


def is_superstring(long: str, short: str):
    in_short_at = 0
    for char in long:
        if char == short[in_short_at]:
            in_short_at += 1
            if in_short_at == len(short):
                return True
    return False


def id_generator():
    num = 0
    while True:
        yield str(num)
        num += 1


def gaussian(x, mu=0, sig=1):
    return np.exp(-np.power(x - mu, 2.0) / (2 * np.power(sig, 2.0)))


def sanitize(string: str) -> str:
    try:
        if string[0] == " ":
            return sanitize(string[1:])
        elif string[-1] == " ":
            return sanitize(string[:-1])
        elif string[-1] == "\n":
            return sanitize(string[:-1])
    except IndexError:
        pass
    return string


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


def key_by_value(dictionary, value, compare_callback=None):
    for key, val in dictionary.items():
        if compare_callback:
            try:
                if compare_callback(val, value):
                    return key
            except AttributeError:
                pass
        else:
            if val == value:
                return key


def sanitize_whitespace_and_symbols(string: str) -> str:
    return string.translate(
        {ord(c): "_" for c in " !@#$%^&*()[]{};:,./<>?\\|`~-=_+"}
    )


def dict_to_string(dictionary: dict) -> str:
    return (
        "{ "
        + ", ".join([f"{key}: {value}" for key, value in dictionary.items()])
        + " }"
    )


def indent(string: str, indentation: int = 1) -> str:
    return "\n".join([indentation * "\t" + line for line in string.split("\n")])
