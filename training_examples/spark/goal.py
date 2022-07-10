# Target
## target code = spark 
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("Spark Example").getOrCreate()


# load_from
## data = load from 'covid_19_data.csv' as csv_with_header 
data = spark.read.format('csv').option("header", True).load('covid_19_data.csv') 

# drop_columns & select_rows & group_by & union & join & sort_by ... descending & describe & show
## on data | drop columns 'Active', 'Country/Region' | select rows 'Confirmed' < 20 | group by 'Deaths' | union other_dataframe | join outer another_df on 'SNo' | sort by 'Recovered' descending | describe | show  
data.drop(['Active', 'Country/Region']).filter('Confirmed' < 20).groupBy(['Deaths']).unionByName(other_dataframe).join(another_df, on=['SNo'], how='outer').sort(['Recovered'], ascending=[False]).describe().show() 

# drop_duplicates & difference & apply max & sort_by ... ascending & head & apply mean & show_schema & save_to csv
## on data | drop duplicates | difference other_df | apply max on 'Deaths' as 'Most deaths' | sort by 'Active' ascending | head 250 | apply mean on 'Active' as 'Average active' | show schema | save to 'training_examples/pandas/save_target.csv' as csv 
data.dropDuplicates().subtract(other_df).agg(max('Deaths').alias('Most deaths')).sort(['Active'], ascending=[True]).head(250).agg(mean('Active').alias('Average active')).printSchema().write.format('csv').save('training_examples/pandas/save_target.csv') 

# group_by & intersection & apply sum & replace_values & apply max & apply min & describe & save_to csv
## on data | group by 'Active' | intersection some_other_df | apply sum on 'Active' as 'Total active' | replace 0 with 'Unknown' | apply max on 'Confirmed' as 'Most confirmed' | apply min on 'Confirmed' as 'Least confirmed' | describe | save to 'training_examples/pandas/save_target.csv' as csv 
data.groupBy(['Active']).intersect(some_other_df).agg(sum('Active').alias('Total active')).replace(0, 'Unknown').agg(max('Confirmed').alias('Most confirmed')).agg(min('Confirmed').alias('Least confirmed')).describe().write.format('csv').save('training_examples/pandas/save_target.csv') 

# drop_columns & intersection & sort_by ... descending & rename_columns & sort_by ... ascending & drop_duplicates & count & show
## on data | drop columns 'Active' | intersection other_other_df | sort by 'Active' descending | rename columns 'Active' to 'Still ill' | sort by 'Still ill' ascending | drop duplicates | count | show 
data.drop(['Active']).intersect(other_other_df).sort(['Active'], ascending=[False]).withColumnRenamed('Active', 'Still ill').sort(['Still ill'], ascending=[True]).dropDuplicates().count().show() 

# create_dataframe & rename_columns & select_columns & append_column & append_column & apply sum & apply mean & select_columns
## this_new_dataframe = create dataframe from data with header 'Confirmed', 'Active', 'Deaths', 'Country/Region' | rename columns 'Active' to 'Still sick' | select columns 'Still sick', 'Active' | append column 0 as 'Zeroes' | append column 'Zeroes' + 1 as 'Ones' | apply sum on 'Zeroes' as 'More zeroes' | apply mean on 'Ones' as 'More ones' | select columns 'Zeroes', 'Ones' 
this_new_dataframe = spark.createDataFrame(data, schema=['Confirmed', 'Active', 'Deaths', 'Country/Region']).withColumnRenamed('Active', 'Still sick').select(['Still sick', 'Active']).withColumn('Zeroes', 0).withColumn('Ones', 'Zeroes' + 1).agg(sum('Zeroes').alias('More zeroes')).agg(mean('Ones').alias('More ones')).select(['Zeroes', 'Ones']) 

# replace_values & difference & select_rows & union & count & save_to json
## on data | replace 12 with 'twelve' | difference 'some other table' | select rows 'Active' > 12 | union one_more_df | count | save to 'training_examples/pandas/save_target.csv' as json 
data.replace(12, 'twelve').subtract('some other table').filter('Active' > 12).unionByName(one_more_df).count().write.format('json').save('training_examples/pandas/save_target.csv') 

# create_dataframe & head & join & apply min & show_schema
## df1984 = create dataframe from data with header 'Active', 'Country/Region' | head 1000 | join right data on 'Country/Region' | apply min on 'Active' as 'Least active' | show schema 
df1984 = spark.createDataFrame(data, schema=['Active', 'Country/Region']).head(1000).join(data, on=['Country/Region'], how='right').agg(min('Active').alias('Least active')).printSchema() 
