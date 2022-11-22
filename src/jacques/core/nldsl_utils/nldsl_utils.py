from typing import Callable, List
from nldsl import grammar
from nldsl.pandas_extension import PandasExpressionRule
from nldsl.core.utils import list_to_string

from ..rule import OverridenRule, Rule
from ...utils import indent, sanitize_whitespace_and_symbols, dict_to_string
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
    function_code = f"@grammar\ndef {name}(code):\n{indent(_grammar)}\n{indent(code_string)}"
    context = _sandbox_context()
    exec(function_code, context)  # pylint: disable=exec-used # no other way
    function = context[name]
    return function


def _sandbox_context() -> dict:
    return _sandbox_context_preset.copy()


def generate_function(rule: Rule) -> Callable:
    # pylint: disable=line-too-long # we have to deal with this in case of string formatting
    sanitized_function_name = sanitize_whitespace_and_symbols(rule.name)
    if isinstance(rule, Rule):
        function_code = f"@grammar(expr=ExpressionRule)\ndef {sanitized_function_name}(pipe, args):\n{indent(_grammar(rule))}\n{indent(rule.nldsl_code)}"
    elif isinstance(rule, OverridenRule):
        grammar = f'"""\nGrammar:\n{indent(rule.dsl)}\n"""'  # pylint: disable=redefined-outer-name
        function_code = f"@grammar(expr=ExpressionRule)\ndef {sanitized_function_name}(pipe, args):\n{indent(grammar)}\n{indent(rule.code)}"
    context = _sandbox_context()
    exec(function_code, context)  # pylint: disable=exec-used # no other way
    function = context[sanitized_function_name]
    return function


def generate_source_from_ruleset(rules: List[Rule]) -> str:
    # pylint: disable=line-too-long # we have to deal with this in case of string formatting
    source = """
from nldsl.core import CodeGenerator
from nldsl import grammar
from nldsl.core import ExpressionRule
from nldsl.core.utils import list_to_string
from jacques.utils import dict_to_string
from typing import List

class CustomCodeGenerator(CodeGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)\n\n
"""
    names = []
    for rule in rules:
        sanitized_function_name = sanitize_whitespace_and_symbols(rule.name)
        names.append(sanitized_function_name)
        if isinstance(rule, Rule):
            function_code = f"@grammar(expr=ExpressionRule)\ndef {sanitized_function_name}(pipe, args):\n{indent(_grammar(rule))}\n{indent(rule.nldsl_code)}"
        elif isinstance(rule, OverridenRule):
            grammar = f'"""\nGrammar:\n{indent(rule.dsl)}\n"""'  # pylint: disable=redefined-outer-name
            function_code = f"@grammar(expr=ExpressionRule)\ndef {sanitized_function_name}(pipe, args):\n{indent(grammar)}\n{indent(rule.code)}"
        source += function_code + "\n\n"
    for name in names:
        source += f"CustomCodeGenerator.register_function({name})\n"
    return source
