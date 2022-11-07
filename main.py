from jacques.core.jacques import Jacques
from jacques.world_knowledge import *
from loguru import logger

logger.add("logs/jacques.log", level="DEBUG")


j = Jacques()

# j.push_examples_from_file("training_examples/spark/easy.py")
# j.push_examples_from_file("training_examples/pandas/easy.py")
j.push_examples_from_file("training_examples/spark/advanced.py")


# ########################################################
# s = """
# ## data = load from 'covid_19_data.csv' as csv_with_header
# data = pd.read_csv("covid_19_data.csv")
# """
# j.push_example(*s.split("\n")[1:3])
# ##########################################################

# ##########################################################
# s = """
# ## on data | group by 'Country/Region' | drop columns 'Country/Region'
# data.groupby(['Country/Region']).drop(columns=['Country/Region'])
# """
# j.push_example(*s.split("\n")[1:3])
##########################################################

# j.encountered("data")
# s = """
# ## on data
# data
# """
# j.push_example(*s.split("\n")[1:3])
# ########################################################
# s = """
# ## on data | group by 'Col'
# data.groupby(['Col'])
# """
# j.push_example(*s.split("\n")[1:3])
# ########################################################
# s = """
# ## on data | drop columns 'Col'
# data.drop(columns=['Col'])
# """
# j.push_example(*s.split("\n")[1:3])
# ########################################################
# s = """
# ## on data | count
# data.shape[0]
# """
# j.push_example(*s.split("\n")[1:3])
# ########################################################


# s = """
# ## on data | group by 'Country/Region' | intersection other_df | drop columns 'Country/Region' | count
# data.groupby(['Country/Region']).merge(other_df).drop(columns=['Country/Region']).shape[0]
# """
# j.push_example(*s.split("\n")[1:3])
# #######################################################

j.process_all_examples()
for rule in j.ruleset.values():
    logger.info(rule)
