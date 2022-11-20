# Target
## target code = spark 
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("Spark Example").getOrCreate()


# load_from
## data = load from 'covid_20_data.csv' as csv_with_header 
data = spark.read.format('csv').option("header", True).load('covid_20_data.csv') 

# create_dataframe & apply min & show_schema & sort_by ... descending
## other_df = create dataframe from data with header 'Country/Region', 'Confirmed' | apply min on 'Confirmed' as 'Min confirmed' | sort by 'Min confirmed' descending | show schema 
other_df = spark.createDataFrame(data, schema=['Country/Region', 'Confirmed']).agg(min('Confirmed').alias('Min confirmed')).sort(['Min confirmed'], ascending=[False]).printSchema() 

# select_rows & select_columns & sort_by ... ascending & save_to csv
## on data | select rows 'Confirmed' > 100 | sort by 'Confirmed' ascending | save to 'save_target.csv' as csv 
data.filter('Confirmed' > 100).sort(['Confirmed'], ascending=[True]).write.format('csv').save('save_target.csv') 

# join & replace_values & append_column & apply sum
## on data | join left other_df on 'Confirmed' | append column 'Confirmed' - 'Deaths' as 'Active' | apply sum on 'Active' as 'Total Active' 
data.join(other_df, on=['Confirmed'], how='left').withColumn('Active', 'Confirmed' - 'Deaths').agg(sum('Active').alias('Total Active')) 

# intersection & difference & replace_values & show
## on data | intersection other_df | difference other_df | replace 0 with 'Unknown' | show 
data.intersect(other_df).subtract(other_df).replace(0, 'Unknown').show() 

# union & head & apply mean & save_to csv
## on data | union other_df | head 150 | apply mean on 'Confirmed' as 'Mean confirmed' | save to 'training_examples/pandas/save_target.csv' as csv 
data.unionByName(other_df).head(150).agg(mean('Confirmed').alias('Mean confirmed')).write.format('csv').save('training_examples/pandas/save_target.csv') 

# select_columns & sort_by ... descending & head & apply mean
## on data | select columns 'Confirmed', 'Deaths', 'Active' | sort by 'Active' descending | head 250 | apply mean on 'Deaths' as 'Mean deaths of top 250' 
data.select(['Confirmed', 'Deaths', 'Active']).sort(['Active'], ascending=[False]).head(250).agg(mean('Deaths').alias('Mean deaths of top 250')) 

# apply max & apply max & drop_columns & save_to json
## on data | apply max on 'Active' as 'Top Active' | apply max on 'Deaths' as 'Most deaths' | drop columns 'Active', 'Deaths' | save to 'training_examples/pandas/save_target.csv' as json 
data.agg(max('Active').alias('Top Active')).agg(max('Deaths').alias('Most deaths')).drop(['Active', 'Deaths']).write.format('json').save('training_examples/pandas/save_target.csv') 

# select_rows & join & group_by & show
## on data | select rows 'Active' > 200 | join right other_df on 'Active', 'Deaths' | group by 'Country/Region' | show 
data.filter('Active' > 200).join(other_df, on=['Active', 'Deaths'], how='right').groupBy(['Country/Region']).show() 

# ~describe~ & apply sum & apply min & show_schema
## on data | apply sum on 'Active' as 'Total active' | apply min on 'Confirmed' as 'Least confirmed' | show schema 
data.agg(sum('Active').alias('Total active')).agg(min('Confirmed').alias('Least confirmed')).printSchema() 

# union & rename_columns & rename_columns & describe
# ## on data | rename columns 'Confirmed' to 'Confident', 'Active' to 'Still ill' | rename columns 'Deaths' to 'Departed' | describe 
# data.withColumnRenamed('Confirmed', 'Confident').withColumnRenamed('Active', 'Still ill').withColumnRenamed('Deaths', 'Departed').describe() 
## on data | rename columns 'Confirmed' to 'Confident' | rename columns 'Deaths' to 'Departed' | describe 
data.withColumnRenamed('Confirmed', 'Confident').withColumnRenamed('Deaths', 'Departed').describe() 

# drop_duplicates & sort_by ... ascending & create_dataframe & count
## no_of_something = create dataframe from data with header 'Confirmed', 'Country/Region', 'Active' | drop duplicates | sort by 'Active' ascending | count 
no_of_something = spark.createDataFrame(data, schema=['Confirmed', 'Country/Region', 'Active']).dropDuplicates().sort(['Active'], ascending=[True]).count() 

# group_by & intersection & drop_columns & count
## on data | group by 'Country/Region' | intersection other_df | drop columns 'Country/Region' | count 
data.groupBy(['Country/Region']).intersect(other_df).drop(['Country/Region']).count() 

# drop_duplicates & append_column & difference & save_to json
## on data | drop duplicates | append column 0 as 'New useless column' | save to 'training_examples/pandas/save_target.csv' as json 
data.dropDuplicates().withColumn('New useless column', 0).write.format('json').save('training_examples/pandas/save_target.csv') 
