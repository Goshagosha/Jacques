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
## on data | apply mean on 'Deaths' as 'Mean deaths' | apply max on 'Confirmed' as 'Max confirmed' 
data.agg({'Deaths' : 'mean'}).rename(columns={'Deaths' : 'Mean deaths'}).agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max confirmed'}) 
"""
dsl, code = s.split("\n")[1:3]
j.push_example(dsl, code)
##########################################################

j.process_all_examples()
pass
