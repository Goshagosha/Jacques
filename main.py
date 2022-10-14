from jacques.core.jacques import Jacques
from jacques.world_knowledge import *


j = Jacques()

# j.push_examples_from_file("training_examples/spark/easy.py")
# j.push_examples_from_file("training_examples/pandas/easy.py")


#########################################################
s = """
## data = load from 'covid_19_data.csv' as csv_with_header
data = pd.read_csv("covid_19_data.csv")
"""
dsl, code = s.split("\n")[1:3]
j.push_example(dsl, code)
##########################################################
# s = """
# ## on data
# data
# """
# dsl, code = s.split("\n")[1:3]
# j.push_example(dsl, code)
##########################################################


j.process_all_examples()
pass
