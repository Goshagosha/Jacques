# Target
## target code = spark 
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("Spark Example").getOrCreate()


# load_from
## data = load from 'covid_19_data.csv' as csv_with_header 
data = spark.read.format('csv').option("header", True).load('covid_19_data.csv') 

# on_dataframe
## on data 
data 

# create_dataframe
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' 
only_country_deaths = spark.createDataFrame(data, schema=['Country/Region', 'Deaths']) 

# save_to csv
## on data | save to 'output.csv' as csv 
data.write.format('csv').save('output.csv') 

# save_to json
## on data | save to 'output.json' as json 
data.write.format('json').save('output.json') 

# union
## united = on data | union only_country_deaths 
united = data.unionByName(only_country_deaths) 

# difference
## differed = on data | difference only_country_deaths 
differed = data.subtract(only_country_deaths) 

# intersection
## intersected = on data | intersection only_country_deaths 
intersected = data.intersect(only_country_deaths) 

# select_columns
## on data | select columns 'SNo', 'ObservationDate' 
data.select(['SNo', 'ObservationDate']) 

# select_rows
## on data | select rows 'SNo' > 100 and 'SNo' < 200 
data.filter('SNo' > 100 & 'SNo' < 200) 

# drop_columns
## on data | drop columns 'Confirmed' 
data.drop(['Confirmed']) 

# join
## on data | join inner only_country_deaths on 'Country/Region' 
data.join(only_country_deaths, on=['Country/Region'], how='inner') 

# group_by
## on data | group by 'Country/Region' 
data.groupBy(['Country/Region']) 

# replace_values
## on data | replace 1 with 0 
data.replace(1, 0) 

# append_column
## on data | append column 0 as 'Empty' 
data.withColumn('Empty', 0) 

# sort_by
## on data | sort by 'Country/Region' ascending 
data.sort(['Country/Region'], ascending=[True]) 

# sort_by
## on data | sort by 'Country/Region' descending 
data.sort(['Country/Region'], ascending=[False]) 

# drop_duplicates
## on data | drop duplicates 
data.dropDuplicates() 

# rename_columns
## on data | rename columns 'Country/Region' to 'Country' 
data.withColumnRenamed('Country/Region', 'Country') 

# show
## on data | show 
data.show() 

# show_schema
## on data | show schema 
data.printSchema() 

# describe
## on data | describe 
data.describe() 

# head
## on data | head 10 
data.head(10) 

# count
## on data | count 
data.count() 

# apply
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' 
data.agg(mean('Confirmed').alias('Mean Confirmed')) 

# apply
## on data | apply sum on 'Confirmed' as 'Total Confirmed' 
data.agg(sum('Confirmed').alias('Total Confirmed')) 

# apply
## on data | apply max on 'Confirmed' as 'Max Confrimed' 
data.agg(max('Confirmed').alias('Max Confrimed')) 

# apply
## on data | apply min on 'Confirmed' as 'Min Confirmed' 
data.agg(min('Confirmed').alias('Min Confirmed')) 
