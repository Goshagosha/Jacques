from typing import Callable
from nldsl import grammar
from nldsl.pandas_extension import PandasExpressionRule, ExpressionRule

from ..rule import OverridenRule, Rule
from ...utils import indent, sanitize_whitespace_and_symbols, dict_to_string
from nldsl.core.utils import list_to_string
from typing import List
from ..nldsl_utils._grammar import _grammar


_sandbox_context_preset = {
    "grammar": grammar,
    "ExpressionRule": PandasExpressionRule,
    "list_to_string": list_to_string,
    "dict_to_string": dict_to_string,
    "List": List,
}


def generate_init_statement(dsl_string: str, code_string: str) -> Callable:
    name = "initialize"
    _grammar = f'"""\nGrammar:\n\t{dsl_string}\n"""'
    code_string = f"return '''{code_string}'''"
    function_code = (
        f"@grammar\ndef {name}(code):\n{indent(_grammar)}\n{indent(code_string)}"
    )
    context = _sandbox_context()
    exec(function_code, context)
    function = context[name]
    return function


def _sandbox_context() -> dict:
    return _sandbox_context_preset.copy()


def generate_function(rule: Rule) -> Callable:
    sanitized_function_name = sanitize_whitespace_and_symbols(rule.name)
    if isinstance(rule, Rule):
        function_code = f"@grammar(expr=ExpressionRule)\ndef {sanitized_function_name}(pipe, args):\n{indent(_grammar(rule))}\n{indent(rule.nldsl_code)}"
    elif isinstance(rule, OverridenRule):
        grammar = f'"""\nGrammar:\n{indent(rule.dsl)}\n"""'
        function_code = f"@grammar(expr=ExpressionRule)\ndef {sanitized_function_name}(pipe, args):\n{indent(grammar)}\n{indent(rule.code)}"
    context = _sandbox_context()
    exec(function_code, context)
    function = context[sanitized_function_name]
    return function
