from ...utils import indent

def _grammar(rule) -> str:
    return f'"""\nGrammar:\n\t{rule.nldsl_dsl}\n{indent(rule.nldsl_grammar_mods)}\n"""'
