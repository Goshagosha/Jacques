from jacques.core.jacques import Jacques
import jacques.world_knowledge as world_knowledge

j = Jacques(world_knowledge)

j.encountered_objects = ["data"]
dsl = "on data | select rows 'Active' > 200 | join right other_df on 'Active', 'Deaths' | group by 'Country/Region' | show"
py = "print(data['Active' > 200].join(other_df, on=['Active', 'Deaths'], how='right').groupby(['Country/Region']))"

# dsl = "on data | join right other_df on 'Active', 'Deaths'"
# py = "data.join(other_df, on=['Active', 'Deaths'], how='right')"

j.push_example(dsl, py)
j.process_all_examples()

for k, v in j.ruleset.items():
    print(v)
