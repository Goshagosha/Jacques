from typing import Callable
from nldsl import grammar
from nldsl.pandas_extension import PandasExpressionRule

from jacques.core.rule import Rule
from jacques.utils import sanitize_whitespace

_sandbox_context_preset = {
    "grammar": grammar,
    "ExpressionRule": PandasExpressionRule,
}


def _sandbox_context() -> dict:
    return _sandbox_context_preset.copy()


def _grammar(rule: Rule) -> str:
    return f'\t"""\n\tGrammar:\n\t\t{rule.nldsl_dsl}\n\t"""'


def generate_function(rule: Rule) -> Callable:
    sanitized_function_name = sanitize_whitespace(rule.name)
    function_code = f'@grammar(expr=ExpressionRule)\ndef {sanitized_function_name}(pipe, args):\n{_grammar(rule)}\n\treturn f"{rule.nldsl_code}"'
    context = _sandbox_context()
    exec(function_code, context)
    function = context[sanitized_function_name]
    return function
