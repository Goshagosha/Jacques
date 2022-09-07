from jacques.core.jacques import Jacques
import jacques.world_knowledge as world_knowledge

j = Jacques(world_knowledge)

# dsl = "on data | select rows 'Active' > 200 | join right other_df on 'Active', 'Deaths' | group by 'Country/Region' | show"
# py = "print(data['Active' > 200].join(other_df, on=['Active', 'Deaths'], how='right').groupby(['Country/Region']))"

# dsl = "on data | join right other_df on 'Active', 'Deaths'"
# py = "data.join(other_df, on=['Active', 'Deaths'], how='right')"

j.encountered_objects = ["data"]

# dsl = "on data | append column 'Confirmed' - 'Deaths' as 'Active' | apply sum on 'Active' as 'Total Active'"
# py = "data.assign(**{'Active': data.apply(lambda row: 'Confirmed' - 'Deaths', axis=0).values}).agg({'Active' : 'sum'}).rename(columns={'Active' : 'Total Active'})"

dsl = "on data | select rows 'Active' > 200 | join right other_df on 'Active', 'Deaths' | group by 'Country/Region' | show"
py = "print(data['Active' > 200].join(other_df, on=['Active', 'Deaths'], how='right').groupby(['Country/Region']))"
j.push_example(dsl, py)

dsl = "on data | append column 'Confirmed' - 'Deaths' as 'Active'"
py = "data.assign(**{'Active': data.apply(lambda row: 'Confirmed' - 'Deaths', axis=0).values})"

j.push_example(dsl, py)
j.process_all_examples()

for k, v in j.ruleset.items():
    print(v)
