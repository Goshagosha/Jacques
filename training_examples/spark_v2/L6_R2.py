# Target
## target code = spark 
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("Spark Example").getOrCreate()

# necessity
## data = load from 'covid_19_data.csv' as csv_with_header 
data = spark.read.format('csv').option("header", True).load('covid_19_data.csv') 

# necessity
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' 
only_country_deaths = spark.createDataFrame(data, schema=['Country/Region', 'Deaths']) 

# load_from & join right & head & rename_columns & apply min & count
## load from 'covid_19_data.csv' as csv_with_header | join right only_country_deaths on 'Country/Region' | head 10 | rename columns 'Confirmed' to 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' | count 
spark.read.format('csv').option("header", True).load('covid_19_data.csv').join(only_country_deaths, on=['Country/Region'], how='right').head(10).withColumnRenamed('Confirmed', 'Deaths').agg(min('Confirmed').alias('Min Confirmed')).count() 

# load_from & apply min & difference & sort_by asc & apply mean & show_schema
## load from 'covid_19_data.csv' as csv_with_header | apply min on 'Confirmed' as 'Min Confirmed' | difference only_country_deaths | sort by 'Confirmed' ascending | apply mean on 'Confirmed' as 'Mean Confirmed' | show schema 
spark.read.format('csv').option("header", True).load('covid_19_data.csv').agg(min('Confirmed').alias('Min Confirmed')).subtract(only_country_deaths).sort(['Confirmed'], ascending=[True]).agg(mean('Confirmed').alias('Mean Confirmed')).printSchema() 

# on & apply sum & head & append_column & apply mean & count & show 
## on data | apply sum on 'Confirmed' as 'Total Confirmed' | head 10 | append column 'Confirmed' - 'Recovered' as 'Deaths' | apply mean on 'Confirmed' as 'Mean Confirmed' | count | show 
data.agg(sum('Confirmed').alias('Total Confirmed')).withColumn('Deaths', 'Confirmed' - 'Recovered').agg(mean('Confirmed').alias('Mean Confirmed')).count().show(10) 

# on & group_by & rename_columns & sort_by desc & select_rows & select_columns & describe
## on data | group by 'Country/Region' | rename columns 'Confirmed' to 'Deaths' | sort by 'Confirmed' descending | select rows 'SNo' > 100 | select columns 'SNo', 'ObservationDate' | describe 
data.groupBy(['Country/Region']).withColumnRenamed('Confirmed', 'Deaths').sort(['Confirmed'], ascending=[False]).filter('SNo' > 100).select(['SNo', 'ObservationDate']).describe() 

# on & drop_columns & apply max & append_column & join inner & replace_values & show_schema
## on data | drop columns 'Confirmed' | apply max on 'Confirmed' as 'Max Confirmed' | append column 'Confirmed' - 'Recovered' as 'Deaths' | join inner only_country_deaths on 'Country/Region' | replace 'Confirmed' with 'Deaths' | show schema 
data.drop(['Confirmed']).agg(max('Confirmed').alias('Max Confirmed')).withColumn('Deaths', 'Confirmed' - 'Recovered').join(only_country_deaths, on=['Country/Region'], how='inner').replace('Confirmed', 'Deaths').printSchema() 

# on & apply max & group_by & sort_by asc & intersection & drop_columns & describe
## on data | apply max on 'Confirmed' as 'Max Confirmed' | group by 'Country/Region' | sort by 'Confirmed' ascending | intersection only_country_deaths | drop columns 'Confirmed' | describe 
data.agg(max('Confirmed').alias('Max Confirmed')).groupBy(['Country/Region']).sort(['Confirmed'], ascending=[True]).intersect(only_country_deaths).drop(['Confirmed']).describe() 

# on & join inner & drop_duplicates & join right & union & select_columns & show 
## on data | join inner only_country_deaths on 'Country/Region' | drop duplicates | join right only_country_deaths on 'Country/Region' | union only_country_deaths | select columns 'SNo', 'ObservationDate' | show 
data.join(only_country_deaths, on=['Country/Region'], how='inner').dropDuplicates().join(only_country_deaths, on=['Country/Region'], how='right').unionByName(only_country_deaths).select(['SNo', 'ObservationDate']).show() 

# create_dataframe & intersection & replace_values & union & save_to csv
## create dataframe from data with header 'Country/Region', 'Deaths' | intersection only_country_deaths | replace 'Confirmed' with 'Deaths' | union only_country_deaths | save to 'output.csv' as csv 
spark.createDataFrame(data, schema=['Country/Region', 'Deaths']).intersect(only_country_deaths).replace('Confirmed', 'Deaths').unionByName(only_country_deaths).write.format('csv').save('output.csv') 

# create_dataframe & apply sum & drop_duplicates & select_rows & difference & save_to json
## create dataframe from data with header 'Country/Region', 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' | drop duplicates | select rows 'SNo' > 100 | difference only_country_deaths | save to 'output.json' as json 
spark.createDataFrame(data, schema=['Country/Region', 'Deaths']).agg(sum('Confirmed').alias('Total Confirmed')).dropDuplicates().filter('SNo' > 100).subtract(only_country_deaths).write.format('json').save('output.json') 

# on & sort_by desc & save_to json
## on data | sort by 'Confirmed' descending | save to 'output.json' as json 
data.sort(['Confirmed'], ascending=[False]).write.format('json').save('output.json') 

