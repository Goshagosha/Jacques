from jacques.core.jacques import Jacques
import jacques.world_knowledge as world_knowledge

j = Jacques(world_knowledge)


j.encountered_objects = ["data"]

j.push_examples_from_file("training_examples/spark/easy.py")


j.process_all_examples()


for k, v in j.ruleset.items():
    print(v)
    print()

# del v
# del k

# print()
# r = j.code_generator("## on data | join right other_df on 'Active', 'Deaths'")
# print(r)
