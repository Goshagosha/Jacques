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

# on & drop_duplicates & difference & apply mean & select_columns & intersection & show_schema
## on data | drop duplicates | difference only_country_deaths | apply mean on 'Confirmed' as 'Mean Confirmed' | select columns 'SNo', 'ObservationDate' | intersection only_country_deaths | show schema 
data.dropDuplicates().subtract(only_country_deaths).agg(mean('Confirmed').alias('Mean Confirmed')).select(['SNo', 'ObservationDate']).intersect(only_country_deaths).printSchema() 

# on & sort_by asc & apply mean & apply sum & union & replace_values & count
## on data | sort by 'Confirmed' ascending | apply mean on 'Confirmed' as 'Mean Confirmed' | apply sum on 'Confirmed' as 'Total Confirmed' | union only_country_deaths | replace 'Confirmed' with 'Deaths' | count 
data.sort(['Confirmed'], ascending=[True]).agg(mean('Confirmed').alias('Mean Confirmed')).agg(sum('Confirmed').alias('Total Confirmed')).unionByName(only_country_deaths).replace('Confirmed', 'Deaths').count() 

# load_from & sort_by asc & drop_columns & join inner & group_by & join right & save_to json
## load from 'covid_19_data.csv' as csv_with_header | sort by 'Confirmed' ascending | drop columns 'Confirmed' | join inner only_country_deaths on 'Country/Region' | group by 'Country/Region' | join right only_country_deaths on 'Country/Region' | save to 'output.json' as json 
spark.read.format('csv').option("header", True).load('covid_19_data.csv').sort(['Confirmed'], ascending=[True]).drop(['Confirmed']).join(only_country_deaths, on=['Country/Region'], how='inner').groupBy(['Country/Region']).join(only_country_deaths, on=['Country/Region'], how='right').write.format('json').save('output.json') 

# load_from & rename_columns & apply max & head & intersection & save_to csv
## load from 'covid_19_data.csv' as csv_with_header | rename columns 'Confirmed' to 'Deaths' | apply max on 'Confirmed' as 'Max Confirmed' | head 10 | intersection only_country_deaths | save to 'output.csv' as csv 
spark.read.format('csv').option("header", True).load('covid_19_data.csv').withColumnRenamed('Confirmed', 'Deaths').agg(max('Confirmed').alias('Max Confirmed')).head(10).intersect(only_country_deaths).write.format('csv').save('output.csv') 

# on & apply min & group_by & select_rows & apply max & append_column & save_to json
## on data | apply min on 'Confirmed' as 'Min Confirmed' | group by 'Country/Region' | select rows 'SNo' > 100 | apply max on 'Confirmed' as 'Max Confirmed' | append column 'Confirmed' - 'Recovered' as 'Deaths' | save to 'output.json' as json 
data.agg(min('Confirmed').alias('Min Confirmed')).groupBy(['Country/Region']).filter('SNo' > 100).agg(max('Confirmed').alias('Max Confirmed')).withColumn('Deaths', 'Confirmed' - 'Recovered').write.format('json').save('output.json') 

# create_dataframe & rename_columns & apply min & sort_by desc & describe & show
## create dataframe from data with header 'Country/Region', 'Deaths' | rename columns 'Confirmed' to 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' | sort by 'Confirmed' descending | describe | show 
spark.createDataFrame(data, schema=['Country/Region', 'Deaths']).withColumnRenamed('Confirmed', 'Deaths').agg(min('Confirmed').alias('Min Confirmed')).sort(['Confirmed'], ascending=[False]).describe().show() 

# create_dataframe & join inner & replace_values & head & show_schema
## create dataframe from data with header 'Country/Region', 'Deaths' | join inner only_country_deaths on 'Country/Region' | replace 'Confirmed' with 'Deaths' | head 10 | show schema 
spark.createDataFrame(data, schema=['Country/Region', 'Deaths']).join(only_country_deaths, on=['Country/Region'], how='inner').replace('Confirmed', 'Deaths').head(10).printSchema() 

