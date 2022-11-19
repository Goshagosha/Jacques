# Target
## target code = spark 
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("Spark Example").getOrCreate()

# load_from & save_to csv
## data = load from 'covid_19_data.csv' as csv_with_header | save to 'output.csv' as csv 
data = spark.read.format('csv').option("header", True).load('covid_19_data.csv').write.format('csv').save('output.csv') 

# create_dataframe & apply min
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' 
only_country_deaths = spark.createDataFrame(data, schema=['Country/Region', 'Deaths']).agg(min('Confirmed').alias('Min Confirmed')) 

# on & sort_by desc & select_columns
## on data | sort by 'Confirmed' descending | select columns 'SNo', 'ObservationDate' 
data.sort(['Confirmed'], ascending=[False]).select(['SNo', 'ObservationDate']) 

# on & difference & union
## on data | difference only_country_deaths | union only_country_deaths 
data.subtract(only_country_deaths).unionByName(only_country_deaths) 

# on & rename_columns & drop_columns
## on data | rename columns 'Confirmed' to 'Deaths' | drop columns 'Confirmed' 
data.withColumnRenamed('Confirmed', 'Deaths').drop(['Confirmed']) 

# on & head & apply max
## on data | head 10 | apply max on 'Confirmed' as 'Max Confirmed' 
data.head(10).agg(max('Confirmed').alias('Max Confirmed')) 

# on & apply mean & save_to json
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | save to 'output.json' as json 
data.agg(mean('Confirmed').alias('Mean Confirmed')).write.format('json').save('output.json') 

# on & drop_duplicates & select_columns
## on data | drop duplicates | select columns 'SNo', 'ObservationDate' 
data.dropDuplicates().select(['SNo', 'ObservationDate']) 

# on & sort_by asc & join inner
## on data | sort by 'Confirmed' ascending | join inner only_country_deaths on 'Country/Region' 
data.sort(['Confirmed'], ascending=[True]).join(only_country_deaths, on=['Country/Region'], how='inner') 

# on & intersection & save_to json
## on data | intersection only_country_deaths | save to 'output.json' as json 
data.intersect(only_country_deaths).write.format('json').save('output.json') 

# on & append_column & show_schema
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' | show schema 
data.withColumn('Deaths', 'Confirmed' - 'Recovered').printSchema() 

# on & replace_values & drop_columns
## on data | replace 'Confirmed' with 'Deaths' | drop columns 'Confirmed' 
data.replace('Confirmed', 'Deaths').drop(['Confirmed']) 

# on & apply mean & save_to csv
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | save to 'output.csv' as csv 
data.agg(mean('Confirmed').alias('Mean Confirmed')).write.format('csv').save('output.csv') 

# on & drop_duplicates & apply min
## on data | drop duplicates | apply min on 'Confirmed' as 'Min Confirmed' 
data.dropDuplicates().agg(min('Confirmed').alias('Min Confirmed')) 

# on & join right & show
## on data | join right only_country_deaths on 'Country/Region' | show 
data.join(only_country_deaths, on=['Country/Region'], how='right').show() 

# on & sort_by asc & apply sum
## on data | sort by 'Confirmed' ascending | apply sum on 'Confirmed' as 'Total Confirmed' 
data.sort(['Confirmed'], ascending=[True]).agg(sum('Confirmed').alias('Total Confirmed')) 

# on & replace_values & describe
## on data | replace 'Confirmed' with 'Deaths' | describe 
data.replace('Confirmed', 'Deaths').describe() 

# on & select_rows & describe
## on data | select rows 'SNo' > 100 | describe 
data.filter('SNo' > 100).describe() 

# on & difference & rename_columns
## on data | difference only_country_deaths | rename columns 'Confirmed' to 'Deaths' 
data.subtract(only_country_deaths).withColumnRenamed('Confirmed', 'Deaths') 

# on & apply max & count
## on data | apply max on 'Confirmed' as 'Max Confirmed' | count 
data.agg(max('Confirmed').alias('Max Confirmed')).count() 

# load_from & union
## load from 'covid_19_data.csv' as csv_with_header | union only_country_deaths 
spark.read.format('csv').option("header", True).load('covid_19_data.csv').unionByName(only_country_deaths) 

# on & select_rows & intersection
## on data | select rows 'SNo' > 100 | intersection only_country_deaths 
data.filter('SNo' > 100).intersect(only_country_deaths) 

# on & count & show
## on data | count | show 
data.count().show() 

# create_dataframe & append_column
## create dataframe from data with header 'Country/Region', 'Deaths' | append column 'Confirmed' - 'Recovered' as 'Deaths' 
spark.createDataFrame(data, schema=['Country/Region', 'Deaths']).withColumn('Deaths', 'Confirmed' - 'Recovered') 

# on & apply sum & group_by
## on data | apply sum on 'Confirmed' as 'Total Confirmed' | group by 'Country/Region' 
data.agg(sum('Confirmed').alias('Total Confirmed')).groupBy(['Country/Region']) 

# on & join right & head
## on data | join right only_country_deaths on 'Country/Region' | head 10 
data.join(only_country_deaths, on=['Country/Region'], how='right').head(10) 

# on & sort_by desc & join inner
## on data | sort by 'Confirmed' descending | join inner only_country_deaths on 'Country/Region' 
data.sort(['Confirmed'], ascending=[False]).join(only_country_deaths, on=['Country/Region'], how='inner') 

# on & group_by & show_schema
## on data | group by 'Country/Region' | show schema 
data.groupBy(['Country/Region']).printSchema() 

