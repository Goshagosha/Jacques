from jacques.core.jacques import Jacques
import jacques.world_knowledge as world_knowledge

j = Jacques(world_knowledge)
j.encountered_objects = ["data"]

# j.push_examples_from_file("training_examples/spark/easy.py")
# j.push_examples_from_file("training_examples/pandas/no_logical_inference.py")

s = """
## on data | show
print(data)
"""
dsl, code = s.split("\n")[1:3]
j.push_example(dsl, code)

s = """
## on data | append column 0 as 'Empty'
data.assign(**{"Empty": data.apply(lambda row: 0, axis=1).values})
"""
dsl, code = s.split("\n")[1:3]
j.push_example(dsl, code)


j.process_all_examples()
