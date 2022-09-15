import sys

sys.path.append(".")

from jacques.core.jacques import Jacques

j = Jacques()
j.encountered_objects = ["data"]


print("WITHOUT CROSS MATCHING:")
dsl = "## on data | save to 'save_target.csv' as csv"
code = "data.write.format('csv').save('save_target.csv')"
j.push_example(dsl, code)
j.process_all_examples()

for k, v in j.ruleset.items():
    print(v)
    print()

print("WITH CROSS MATCHING:")
dsl = "on data | show"
code = "print(data)"
j.push_example(dsl, code)
j.process_all_examples()


for k, v in j.ruleset.items():
    print(v)
    print()
