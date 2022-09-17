from jacques.core.jacques import Jacques
from jacques.world_knowledge import *


j = Jacques()

# j.push_examples_from_file("training_examples/spark/easy.py")
j.push_examples_from_file("training_examples/pandas/easy.py")

# j.encountered("data")
# j.encountered("other_country_deaths")

# ###########################################################
# s = """
# ## on data
# data
# """
# dsl, code = s.split("\n")[1:3]
# j.push_example(dsl, code)
# ###########################################################
# s = """
# ## on other_country_deaths
# other_country_deaths
# """
# dsl, code = s.split("\n")[1:3]
# j.push_example(dsl, code)
# ##########################################################
# s = """
# ## differed = on data | difference only_country_deaths
# differed = data[~data.isin(only_country_deaths).all(1)]
# """
# dsl, code = s.split("\n")[1:3]
# j.push_example(dsl, code)
# ###########################################################

j.process_all_examples()
pass
