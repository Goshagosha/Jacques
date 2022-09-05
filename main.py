from jacques.core.jacques import Jacques
import jacques.world_knowledge as world_knowledge

j = Jacques(world_knowledge)

j.encountered_objects = ["data"]
# dsl = "on data | join right other_df on 'Active', 'Deaths' | group by 'Country/Region' | show"
# py = "print(data.join(other_df, on=['Active', 'Deaths'], how='right').groupby(['Country/Region']))"

dsl = "on data | select rows 'Active' > 200"
py = "data['Active' > 200]"

# This must be a bug in original
# dsl = "on data | select rows 'SNo' > 100 and 'SNo' < 200"
# Wrong:
# py = 'data["SNo" > 100 & "SNo" < 200]'
# Correct:
# py = 'data[("SNo" > 100) & ("SNo" < 200)]'

j.push_example(dsl, py)
j.process_all_examples()
for k, v in j.ruleset.items():
    print(v)
