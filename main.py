from jacques.core.jacques import Jacques
from jacques.world_knowledge import *
from loguru import logger

logger.add("logs/jacques.log", level="DEBUG")


j = Jacques()

# j.push_examples_from_file("training_examples/spark/easy.py")
# j.push_examples_from_file("training_examples/pandas/easy.py")
j.push_examples_from_file("training_examples/pandas/advanced.py")


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

# j.encountered("data")

# s = """
# ## df1 = create dataframe from data with header 'Country/Region' | save to 'save_target.csv' as csv
# df1 = pd.DataFrame(data, columns=['Country/Region']).to_csv('save_target.csv')
# """
# j.push_example(*s.split("\n")[1:3])
########################################################

j.process_all_examples()
