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

# on & select_columns & apply mean & group_by & save_to json
## on data | select columns 'SNo', 'ObservationDate' | apply mean on 'Confirmed' as 'Mean Confirmed' | group by 'Country/Region' | save to 'output.json' as json 
data.select(['SNo', 'ObservationDate']).agg(mean('Confirmed').alias('Mean Confirmed')).groupBy(['Country/Region']).write.format('json').save('output.json') 

# load_from & head & apply min & show
## load from 'covid_19_data.csv' as csv_with_header | head 10 | apply min on 'Confirmed' as 'Min Confirmed' | show 
spark.read.format('csv').option("header", True).load('covid_19_data.csv').agg(min('Confirmed').alias('Min Confirmed')).show(10) 

# on & union & drop_duplicates & join right & show_schema
## on data | union only_country_deaths | drop duplicates | join right only_country_deaths on 'Country/Region' | show schema 
data.unionByName(only_country_deaths).dropDuplicates().join(only_country_deaths, on=['Country/Region'], how='right').printSchema() 

# on & difference & replace_values & apply mean & rename_columns
## on data | difference only_country_deaths | replace 'Confirmed' with 'Deaths' | apply mean on 'Confirmed' as 'Mean Confirmed' | rename columns 'Confirmed' to 'Deaths' 
data.subtract(only_country_deaths).replace('Confirmed', 'Deaths').agg(mean('Confirmed').alias('Mean Confirmed')).withColumnRenamed('Confirmed', 'Deaths') 

# on & sort_by desc & join inner & apply sum & save_to csv
## on data | sort by 'Confirmed' descending | join inner only_country_deaths on 'Country/Region' | apply sum on 'Confirmed' as 'Total Confirmed' | save to 'output.csv' as csv 
data.sort(['Confirmed'], ascending=[False]).join(only_country_deaths, on=['Country/Region'], how='inner').agg(sum('Confirmed').alias('Total Confirmed')).write.format('csv').save('output.csv') 

# on & append_column & rename_columns & replace_values & intersection
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' | rename columns 'Confirmed' to 'Deaths' | replace 'Confirmed' with 'Deaths' | intersection only_country_deaths 
data.withColumn('Deaths', 'Confirmed' - 'Recovered').withColumnRenamed('Confirmed', 'Deaths').replace('Confirmed', 'Deaths').intersect(only_country_deaths) 

# create_dataframe & apply sum & drop_columns & save_to csv
## create dataframe from data with header 'Country/Region', 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' | drop columns 'Confirmed' | save to 'output.csv' as csv 
spark.createDataFrame(data, schema=['Country/Region', 'Deaths']).agg(sum('Confirmed').alias('Total Confirmed')).drop(['Confirmed']).write.format('csv').save('output.csv') 

# on & join right & append_column & count & show
## on data | join right only_country_deaths on 'Country/Region' | append column 'Confirmed' - 'Recovered' as 'Deaths' | count | show 
data.join(only_country_deaths, on=['Country/Region'], how='right').withColumn('Deaths', 'Confirmed' - 'Recovered').count().show() 

# on & group_by & sort_by asc & head & describe
## on data | group by 'Country/Region' | sort by 'Confirmed' ascending | head 10 | describe 
data.groupBy(['Country/Region']).sort(['Confirmed'], ascending=[True]).head(10).describe() 

# on & join inner & select_rows & apply max & show_schema
## on data | join inner only_country_deaths on 'Country/Region' | select rows 'SNo' > 100 | apply max on 'Confirmed' as 'Max Confirmed' | show schema 
data.join(only_country_deaths, on=['Country/Region'], how='inner').filter('SNo' > 100).agg(max('Confirmed').alias('Max Confirmed')).printSchema() 

# load_from & intersection & sort_by asc & select_rows
## load from 'covid_19_data.csv' as csv_with_header | intersection only_country_deaths | sort by 'Confirmed' ascending | select rows 'SNo' > 100 
spark.read.format('csv').option("header", True).load('covid_19_data.csv').intersect(only_country_deaths).sort(['Confirmed'], ascending=[True]).filter('SNo' > 100) 

# create_dataframe & drop_columns & select_columns & describe
## create dataframe from data with header 'Country/Region', 'Deaths' | drop columns 'Confirmed' | select columns 'SNo', 'ObservationDate' | describe 
spark.createDataFrame(data, schema=['Country/Region', 'Deaths']).drop(['Confirmed']).select(['SNo', 'ObservationDate']).describe() 

# on & apply max & apply min & union & save_to json
## on data | apply max on 'Confirmed' as 'Max Confirmed' | apply min on 'Confirmed' as 'Min Confirmed' | union only_country_deaths | save to 'output.json' as json 
data.agg(max('Confirmed').alias('Max Confirmed')).agg(min('Confirmed').alias('Min Confirmed')).unionByName(only_country_deaths).write.format('json').save('output.json') 

# on & sort_by desc & drop_duplicates & difference & count
## on data | sort by 'Confirmed' descending | drop duplicates | difference only_country_deaths | count 
data.sort(['Confirmed'], ascending=[False]).dropDuplicates().subtract(only_country_deaths).count() 

