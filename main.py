from jacques.core.jacques import Jacques
from jacques.world_knowledge import *


j = Jacques()

# j.push_examples_from_file("training_examples/spark/easy.py")
# j.push_examples_from_file("training_examples/pandas/easy.py")

j.encountered("data")

##########################################################
s = """
## on data | show
print(data)
"""
dsl, code = s.split("\n")[1:3]
j.push_example(dsl, code)
#########################################################
s = """
## on data | select rows 'Deaths' > 100
data['Deaths' > 100]
"""
dsl, code = s.split("\n")[1:3]
j.push_example(dsl, code)
##########################################################
s = """
## on data | append column 'Confirmed' - 'Deaths' as 'Survivors'
data.assign(**{'Survivors': data.apply(lambda row: 'Confirmed' - 'Deaths', axis=1).values})
"""
dsl, code = s.split("\n")[1:3]
j.push_example(dsl, code)
##########################################################


j.process_all_examples()
pass
