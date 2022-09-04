from typing import Dict
import jacques.world_knowledge as wk
import logging

from main import Jacques


def process_fresh(dsl: str, py: str, encountered_objects=None) -> Jacques:
    j = Jacques(wk)
    if encountered_objects:
        j.encountered_objects = encountered_objects
    j.push_example(dsl, py)
    j.process_all_examples()
    return j


def test_ObjectAccess():
    dsl = "on data"
    py = "data"
    rules = process_fresh(dsl, py, ["data"]).ruleset
    assert "on" in rules.keys()
    assert rules["on"].code_source == "<ARG0>"
    assert rules["on"].dsl_source == "on <ARG0>"


def test_VariableMemory():
    dsl = "data = load from 'covid_19_data.csv' as csv_with_header"
    py = "data = pd.read_csv('covid_19_data.csv')"
    j = process_fresh(dsl, py)
    assert len(j.encountered_objects) == 1
    assert "data" in j.encountered_objects


def test_GroupBy():
    dsl = "on data | group by 'Country/Region'"
    py = "data.groupby(['Country/Region'])"
    rules = process_fresh(dsl, py, ["data"]).ruleset
    pass


def test_MemoryAndAccess():
    j = Jacques(wk)
    dsl = "data = load from 'covid_19_data.csv' as csv_with_header"
    py = "data = pd.read_csv('covid_19_data.csv')"
    j.push_example(dsl, py)
    dsl = "on data"
    py = "data"
    j.push_example(dsl, py)
    j.process_all_examples()
    for k, v in j.ruleset.items():
        j.ruleset[k] = v.unset_unknowns()
    assert len(j.encountered_objects) == 1
    assert "data" in j.encountered_objects
