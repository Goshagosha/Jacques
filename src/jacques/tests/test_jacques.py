from ..core.jacques import Jacques
import pytest


@pytest.mark.parametrize(
    "dsl,py,encountered_objects",
    [
        ("## on data", "data", "data"),
    ],
)
def test_simple_rule(dsl: str, py: str, encountered_objects) -> Jacques:
    j = Jacques()
    if encountered_objects:
        j.encountered_objects = encountered_objects
    j.push_example(dsl, py)
    j.process_all_examples()
    assert j.get_rule_by_name("on") is not None


def test_jacques() -> Jacques:
    j = Jacques()
    j.push_example("## data = foobar", 'data = load_object("foobar")')
    j.process_all_examples()
    assert "data" in j.encountered_objects
    assert len(j.encountered_objects) == 1
