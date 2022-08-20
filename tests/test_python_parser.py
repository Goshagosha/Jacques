from jacques.jast import (
    ExpressionArgument,
    NumberArgument,
    OperationArgument,
    StringArgument,
)
from tests.helpers import draw_test_result, pp


def test_StringArgument():
    t = pp('print("foobar")')
    draw_test_result(t, "StringArgument")
    assert len(t.arguments) == 1
    assert isinstance(t.arguments[0], StringArgument)
    assert str(t.arguments[0]) == "foobar"


def test_BoolOp_two_children():
    t = pp("'SNo' > 100 and 'SNo' < 200")
    draw_test_result(t, "BoolOp_two_children")
    t = t.arguments[0]
    assert isinstance(t, ExpressionArgument)
    assert isinstance(t.value[0], OperationArgument)
    assert isinstance(t.value[2], OperationArgument)
    assert isinstance(t.value[0].value[0], StringArgument)
    assert isinstance(t.value[0].value[2], NumberArgument)


def test_BoolOp():
    t = pp("True and True")
    draw_test_result(t, "BoolOp")
    assert len(t.arguments) == 1
    assert isinstance(t.arguments[0], ExpressionArgument)
    assert isinstance(t.arguments[0].value[0], StringArgument)
    assert isinstance(t.arguments[0].value[2], StringArgument)


def test_Non_Linear():
    t = pp("data.drop_duplicates().agg(max('Confirmed').alias('Max Confrimed'))")
    draw_test_result(t, "Non_Linear")
    assert t.command == "agg"
    assert t.children[0].command == "drop_duplicates"
    assert t.children[1].command == "alias"
