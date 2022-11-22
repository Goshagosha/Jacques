import os
from src.jacques.core.jacques import Jacques
from src.jacques.constants import *
from loguru import logger


def no_latex(record):
    try:
        return not record["extra"]["latex"]
    except KeyError:
        return True


try:
    os.remove("logs/jacques.log")
except FileNotFoundError:
    pass
logger._core.handlers[0]._filter = no_latex
logger.add("logs/jacques.log", level="DEBUG", filter=no_latex)

j = Jacques()


j.encountered("data")

s = """
## on data | save to 'output.csv' as csv
data.to_csv('output.csv') 
"""
j.push_example(*s.split("\n")[1:3])

s = """
## on data | save to 'output.json' as json
data.to_json('output.json') 
"""
j.push_example(*s.split("\n")[1:3])

j.process_all_examples()

print(j.code_generator("save to 'somewhere.csv' as csv"))
