import os
from src.jacques.core.jacques import Jacques
from jacques.constants import *
from loguru import logger

def no_latex(record):
    try:
        return not record['extra']['latex']
    except KeyError:
        return True

try:
    os.remove('logs/jacques.log')
except FileNotFoundError:
    pass
logger._core.handlers[0]._filter = no_latex
logger.add("logs/jacques.log", level="DEBUG", filter=no_latex)

j = Jacques()


# j.push_examples_from_file("training_examples/pandas_v2/L6_R2.py")
j.encountered("data")

s = """
## on data
data
"""
j.push_example(*s.split("\n")[1:3])

s = """
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' 
data.with_column((pl.col("Confirmed") - pl.col("Recovered")).alias("Deaths"))
"""
j.push_example(*s.split("\n")[1:3])

# s = """
# ## on data | group by 'Country/Region' apply mean on 'Confirmed' as 'Mean Confirmed'
# data.groupby("Country/Region").agg(pl.mean("Confirmed").alias("Mean Confirmed"))
# """
# j.push_example(*s.split("\n")[1:3])

# s = """
# ## on data | group by 'Country/Region' apply sum on 'Confirmed' as 'Total Confirmed'
# data.groupby("Country/Region").agg(pl.sum("Confirmed").alias("Total Confirmed"))
# """
# j.push_example(*s.split("\n")[1:3])

# s = """
# ## on data | group by 'Country/Region' apply max on 'Confirmed' as 'Max Confirmed'
# data.groupby("Country/Region").agg(pl.max("Confirmed").alias("Max Confirmed"))
# """
# j.push_example(*s.split("\n")[1:3])

# s = """
# ## on data | group by 'Country/Region' apply min on 'Confirmed' as 'Min Confirmed'
# data.groupby("Country/Region").agg(pl.min("Confirmed").alias("Min Confirmed"))
# """
# j.push_example(*s.split("\n")[1:3])

# j.push_examples_from_file("training_examples/pandas/no_logical_inference.py")

# #######################################################
# s = """
# ## data = load from 'covid_19_data.csv' as csv_with_header
# data = pd.read_csv("covid_19_data.csv")
# """
# j.push_example(*s.split("\n")[1:3])

# """
# j.push_example(*s.split("\n")[1:3])
##########################################################
# j.encountered("data")
# # j.encountered("df1")

# ##########################################################
# s = """
# ## on data
# data
# """
# j.push_example(*s.split("\n")[1:3])
# ####################################################
# s = """ 
# ## on data | select rows 'SNo' > 100
# data[("SNo" > 100)]
# """
# j.push_example(*s.split("\n")[1:3])
# ######################################################
# s = """ 
# ## on data | select rows 'SNo' > 100
# data[("SNo" > 100)]
# """
# j.push_example(*s.split("\n")[1:3])
######################################################
# # s = """
# # ## on data | union other_df 
# # pd.concat([data, other_df])
# """
# j.push_example(*s.split("\n")[1:3])
#########################################################
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
