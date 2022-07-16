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
