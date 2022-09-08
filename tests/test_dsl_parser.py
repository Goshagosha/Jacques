from typing import Dict
import jacques.world_knowledge as wk

from main import Jacques


def test_Reassemble():
    j = Jacques(world_knowledge=wk)
    dsl = "on data"
    jast = j.dsl_parser.parse(dsl)
    assert jast.jacques_dsl() == dsl


def test_WithLists():
    j = Jacques(world_knowledge=wk)
    dsl = "no_of_something = create dataframe from data with header 'Confirmed', 'Country/Region', 'Active'"
    jast = j.dsl_parser.parse(dsl)
    assert jast.jacques_dsl() == dsl
    assert len(jast.mapping) == 9
    assert len(jast.deconstructed) == 9
