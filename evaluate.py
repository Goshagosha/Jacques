import sys
from src.jacques.core.rule import ConditionalRule
from src.jacques.core.jacques import Jacques
from src.jacques.world_knowledge import *
from loguru import logger

def no_latex(record):
    try:
        return not record['extra']['latex']
    except KeyError:
        return True

rules_to_learn = {
    "load from": 1,
    # "create dataframe from": 1,
    "create dataframe with header": 1,
    "save to": 2,
    "union": 1,
    # "difference": 1,
    # "intersection": 1,
    "select columns": 1,
    "select rows": 1,
    "drop columns": 1,
    "join": 2,
    "group by": 1,
    "apply": 4,
    "replace": 1,
    "append column": 1,
    "sort by": 2,
    "drop duplicates": 1,
    "rename columns": 1,
    "show": 1,
    "show schema": 1,
    "describe": 1,
    "head": 1,
    "count": 1,
}

if __name__ == "__main__":
    filepath = sys.argv[1]
    logname = filepath.split("/")[-2] + '_' + filepath.split("/")[-1].split(".")[0]
    logger._core.handlers[0]._filter = no_latex
    logger.add(f"logs/{logname}.log", level="INFO", filter=no_latex)
    j = Jacques()
    j.push_examples_from_file(filepath)
    j.process_all_examples()
    for rule in rules_to_learn:
        learned = j.get_rule_by_name(rule)
        if not learned:
            logger.info(f"Expected rule '{rule}' not learned")
        else:
            choices = rules_to_learn[rule]
            if isinstance(learned, ConditionalRule):
                if len(learned.choices) != choices:
                    logger.info(f"Expected {choices} options for rule '{rule}', got {len(learned.options)}")
            else:
                if choices > 1:
                    logger.info(f"Expected {choices} options for rule '{rule}', but it is not ConditionalRule")

