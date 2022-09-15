from jacques.core.jacques import Jacques
import jacques.world_knowledge as world_knowledge


j = Jacques(world_knowledge)

# j.push_examples_from_file("training_examples/spark/easy.py")
j.push_examples_from_file("training_examples/pandas/no_logical_inference.py")


# ###########################################################
# s = """
# ## data = load from 'covid_19_data.csv' as csv_with_header
# data = pd.read_csv('covid_19_data.csv')
# """
# dsl, code = s.split("\n")[1:3]
# j.push_example(dsl, code)
# ###########################################################
# s = """
# ## on data
# data
# """
# dsl, code = s.split("\n")[1:3]
# j.push_example(dsl, code)
# ###########################################################
# s = """
# ## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths'
# only_country_deaths = pd.DataFrame(data, columns=['Country/Region', 'Deaths'])
# """
# dsl, code = s.split("\n")[1:3]
# j.push_example(dsl, code)
# ###########################################################
# s = """
# ## united = on data | union only_country_deaths
# united = pd.concat([data, only_country_deaths])
# """
# dsl, code = s.split("\n")[1:3]
# j.push_example(dsl, code)
# ###########################################################

j.process_all_examples()
pass
