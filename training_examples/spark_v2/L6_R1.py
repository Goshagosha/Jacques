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

# on & apply mean & apply max & drop_duplicates & difference & count & show
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | apply max on 'Confirmed' as 'Max Confirmed' | drop duplicates | difference only_country_deaths | count | show 
data.agg(mean('Confirmed').alias('Mean Confirmed')).agg(max('Confirmed').alias('Max Confirmed')).dropDuplicates().subtract(only_country_deaths).count().show() 

# on & drop_columns & union & select_rows & select_columns & rename_columns & save_to json
## on data | drop columns 'Confirmed' | union only_country_deaths | select rows 'SNo' > 100 | select columns 'SNo', 'ObservationDate' | rename columns 'Confirmed' to 'Deaths' | save to 'output.json' as json 
data.drop(['Confirmed']).unionByName(only_country_deaths).filter('SNo' > 100).select(['SNo', 'ObservationDate']).withColumnRenamed('Confirmed', 'Deaths').write.format('json').save('output.json') 

# load_from & intersection & join inner & sort_by asc & apply min & describe
## load from 'covid_19_data.csv' as csv_with_header | intersection only_country_deaths | join inner only_country_deaths on 'Country/Region' | sort by 'Confirmed' ascending | apply min on 'Confirmed' as 'Min Confirmed' | describe 
spark.read.format('csv').option("header", True).load('covid_19_data.csv').intersect(only_country_deaths).join(only_country_deaths, on=['Country/Region'], how='inner').sort(['Confirmed'], ascending=[True]).agg(min('Confirmed').alias('Min Confirmed')).describe() 

# create_dataframe & apply sum & join right & head & replace_values & save_to csv
## create dataframe from data with header 'Country/Region', 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' | join right only_country_deaths on 'Country/Region' | head 10 | replace 'Confirmed' with 'Deaths' | save to 'output.csv' as csv 
spark.createDataFrame(data, schema=['Country/Region', 'Deaths']).agg(sum('Confirmed').alias('Total Confirmed')).join(only_country_deaths, on=['Country/Region'], how='right').head(10).replace('Confirmed', 'Deaths').write.format('csv').save('output.csv') 

# on & group_by & append_column & sort_by desc & show_schema
## on data | group by 'Country/Region' | append column 'Confirmed' - 'Recovered' as 'Deaths' | sort by 'Confirmed' descending | show schema 
data.groupBy(['Country/Region']).withColumn('Deaths', 'Confirmed' - 'Recovered').sort(['Confirmed'], ascending=[False]).printSchema() 

