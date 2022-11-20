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

# load_from & intersection & apply sum & show
## load from 'covid_19_data.csv' as csv_with_header | intersection only_country_deaths | apply sum on 'Confirmed' as 'Total Confirmed' | show 
spark.read.format('csv').option("header", True).load('covid_19_data.csv').intersect(only_country_deaths).agg(sum('Confirmed').alias('Total Confirmed')).show() 

# on & sort_by desc & apply min & difference & show
## on data | sort by 'Confirmed' descending | apply min on 'Confirmed' as 'Min Confirmed' | difference only_country_deaths | show 
data.sort(['Confirmed'], ascending=[False]).agg(min('Confirmed').alias('Min Confirmed')).subtract(only_country_deaths).show() 

# on & difference & apply max & select_columns & group_by
## on data | difference only_country_deaths | apply max on 'Confirmed' as 'Max Confirmed' | select columns 'SNo', 'ObservationDate' | group by 'Country/Region' 
data.subtract(only_country_deaths).agg(max('Confirmed').alias('Max Confirmed')).select(['SNo', 'ObservationDate']).groupBy(['Country/Region']) 

# create_dataframe & join right & rename_columns & group_by
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | join right only_country_deaths on 'Country/Region' | rename columns 'Confirmed' to 'Deaths' | group by 'Country/Region' 
only_country_deaths = spark.createDataFrame(data, schema=['Country/Region', 'Deaths']).join(only_country_deaths, on=['Country/Region'], how='right').withColumnRenamed('Confirmed', 'Deaths').groupBy(['Country/Region']) 

# on & apply max & apply mean & select_rows & count
## on data | apply max on 'Confirmed' as 'Max Confirmed' | apply mean on 'Confirmed' as 'Mean Confirmed' | select rows 'SNo' > 100 | count 
data.agg(max('Confirmed').alias('Max Confirmed')).agg(mean('Confirmed').alias('Mean Confirmed')).filter('SNo' > 100).count() 

# on & head & replace_values & append_column & show_schema
## on data | head 10 | replace 'Confirmed' with 'Deaths' | append column 'Confirmed' - 'Recovered' as 'Deaths' | show schema 
data.head(10).replace('Confirmed', 'Deaths').withColumn('Deaths', 'Confirmed' - 'Recovered').printSchema() 

# on & union & join inner & sort_by desc & save_to csv
## on data | union only_country_deaths | join inner only_country_deaths on 'Country/Region' | sort by 'Confirmed' descending | save to 'output.csv' as csv 
data.unionByName(only_country_deaths).join(only_country_deaths, on=['Country/Region'], how='inner').sort(['Confirmed'], ascending=[False]).write.format('csv').save('output.csv') 

# on & rename_columns & intersection & apply sum & show_schema
## on data | rename columns 'Confirmed' to 'Deaths' | intersection only_country_deaths | apply sum on 'Confirmed' as 'Total Confirmed' | show schema 
data.withColumnRenamed('Confirmed', 'Deaths').intersect(only_country_deaths).agg(sum('Confirmed').alias('Total Confirmed')).printSchema() 

# on & drop_columns & head & join right & count
## on data | drop columns 'Confirmed' | head 10 | join right only_country_deaths on 'Country/Region' | count 
data.drop(['Confirmed']).head(10).join(only_country_deaths, on=['Country/Region'], how='right').count() 

# load_from & drop_duplicates & sort_by asc & save_to csv
## load from 'covid_19_data.csv' as csv_with_header | drop duplicates | sort by 'Confirmed' ascending | save to 'output.csv' as csv 
spark.read.format('csv').option("header", True).load('covid_19_data.csv').dropDuplicates().sort(['Confirmed'], ascending=[True]).write.format('csv').save('output.csv') 

# on & describe & save_to json
## on data | describe | save to 'output.json' as json 
data.describe().write.format('json').save('output.json') 

