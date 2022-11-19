# Target
## target code = spark 
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("Spark Example").getOrCreate()

# load_from & apply min
## data = load from 'covid_19_data.csv' as csv_with_header | apply min on 'Confirmed' as 'Min Confirmed' 
data = spark.read.format('csv').option("header", True).load('covid_19_data.csv').agg(min('Confirmed').alias('Min Confirmed')) 

# create_dataframe & head
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | head 10 
only_country_deaths = spark.createDataFrame(data, schema=['Country/Region', 'Deaths']).head(10) 

# on & intersection & sort_by desc
## on data | intersection only_country_deaths | sort by 'Confirmed' descending 
data.intersect(only_country_deaths).sort(['Confirmed'], ascending=[False]) 

# on & apply mean & replace_values
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | replace 'Confirmed' with 'Deaths' 
data.agg(mean('Confirmed').alias('Mean Confirmed')).replace('Confirmed', 'Deaths') 

# on & select_columns & select_rows
## on data | select columns 'SNo', 'ObservationDate' | select rows 'SNo' > 100 
data.select(['SNo', 'ObservationDate']).filter('SNo' > 100) 

# on & join inner & count
## on data | join inner only_country_deaths on 'Country/Region' | count 
data.join(only_country_deaths, on=['Country/Region'], how='inner').count() 

# on & union & save_to json
## on data | union only_country_deaths | save to 'output.json' as json 
data.unionByName(only_country_deaths).write.format('json').save('output.json') 

# on & sort_by asc & show
## on data | sort by 'Confirmed' ascending | show 
data.sort(['Confirmed'], ascending=[True]).show() 

# on & apply sum & show_schema
## on data | apply sum on 'Confirmed' as 'Total Confirmed' | show schema 
data.agg(sum('Confirmed').alias('Total Confirmed')).printSchema() 

# on & group_by & save_to csv
## on data | group by 'Country/Region' | save to 'output.csv' as csv 
data.groupBy(['Country/Region']).write.format('csv').save('output.csv') 

# on & drop_columns & describe
## on data | drop columns 'Confirmed' | describe 
data.drop(['Confirmed']).describe() 

# on & join right & drop_duplicates
## on data | join right only_country_deaths on 'Country/Region' | drop duplicates 
data.join(only_country_deaths, on=['Country/Region'], how='right').dropDuplicates() 

# on & apply max & rename_columns
## on data | apply max on 'Confirmed' as 'Max Confirmed' | rename columns 'Confirmed' to 'Deaths' 
data.agg(max('Confirmed').alias('Max Confirmed')).withColumnRenamed('Confirmed', 'Deaths') 

# on & difference & append_column
## on data | difference only_country_deaths | append column 'Confirmed' - 'Recovered' as 'Deaths' 
data.subtract(only_country_deaths).withColumn('Deaths', 'Confirmed' - 'Recovered') 

