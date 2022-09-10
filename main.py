from jacques.core.jacques import Jacques
import jacques.world_knowledge as world_knowledge

j = Jacques(world_knowledge)


# j.encountered_objects = ["data", "only_country_deaths"]

# j.push_examples_from_file("training_examples/spark/no_logical_inference.py")
j.push_examples_from_file("training_examples/pandas/no_logical_inference.py")

# ## united = on data | union only_country_deaths
# united = pd.concat([data, only_country_deaths])

# s = """
# ## on data | replace 1 with 0
# data.replace(1, 0)
# """

# dsl, code = s.split("\n")[1:3]


# j.push_example(dsl, code)

j.process_all_examples()


for k, v in j.ruleset.items():
    print(v)
    print()

# del v
# del k

# print()
# r = j.code_generator("## smth = on data | show")
# print(r)
