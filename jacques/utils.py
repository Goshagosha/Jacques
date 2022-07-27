import numpy as np


def is_float(string):
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
