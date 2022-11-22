
from nldsl.core import CodeGenerator
from nldsl import grammar
from nldsl.core import ExpressionRule
from nldsl.core.utils import list_to_string
from jacques.utils import dict_to_string
from typing import List

class CustomCodeGenerator(CodeGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@grammar(expr=ExpressionRule)
def on(pipe, args):
	"""
	Grammar:
		on $arg0
		
	"""
	
	return f"{args['arg0']}"

@grammar(expr=ExpressionRule)
def load_from(pipe, args):
	"""
	Grammar:
		load from $arg0 as csv_with_header
		
	"""
	
	return f"pd.read_csv({args['arg0']})"

CustomCodeGenerator.register_function(on)
CustomCodeGenerator.register_function(load_from)
