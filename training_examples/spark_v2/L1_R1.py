# Target
## target code = spark 
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("Spark Example").getOrCreate()

# load_from
## data = load from 'covid_19_data.csv' as csv_with_header 
data = spark.read.format('csv').option("header", True).load('covid_19_data.csv') 

# create_dataframe
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' 
only_country_deaths = spark.createDataFrame(data, schema=['Country/Region', 'Deaths']) 

# on & select_columns
## on data | select columns 'SNo', 'ObservationDate' 
data.select(['SNo', 'ObservationDate']) 

# on & save_to csv
## on data | save to 'output.csv' as csv 
data.write.format('csv').save('output.csv') 

# on & save_to json
## on data | save to 'output.json' as json 
data.write.format('json').save('output.json') 

# on & difference
## on data | difference 
data.subtract(only_country_deaths) 

# on & group_by
## on data | group by 'Country/Region' 
data.groupBy(['Country/Region']) 

# on & apply mean
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' 
data.agg(mean('Confirmed').alias('Mean Confirmed')) 

# on & append_column
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' 
data.withColumn('Deaths', 'Confirmed' - 'Recovered') 

# on & apply sum
## on data | apply sum on 'Confirmed' as 'Total Confirmed' 
data.agg(sum('Confirmed').alias('Total Confirmed')) 

# on & head
## on data | head 10 
data.head(10) 

# on & join right
## on data | join right only_country_deaths on 'Country/Region' 
data.join(only_country_deaths, on=['Country/Region'], how='right') 

# on & drop_columns
## on data | drop columns 'Confirmed' 
data.drop(['Confirmed']) 

# on & replace_values
## on data | replace 'Confirmed' with 'Deaths' 
data.replace('Confirmed', 'Deaths') 

# on & rename_columns
## on data | rename columns 'Confirmed' to 'Deaths' 
data.withColumnRenamed('Confirmed', 'Deaths') 

# on & intersection
## on data | intersection only_country_deaths 
data.intersect(only_country_deaths) 

# on & show_schema
## on data | show schema 
data.printSchema() 

# on & apply max
## on data | apply max on 'Confirmed' as 'Max Confirmed' 
data.agg(max('Confirmed').alias('Max Confirmed')) 

# on & join inner
## on data | join inner only_country_deaths on 'Country/Region' 
data.join(only_country_deaths, on=['Country/Region'], how='inner') 

# on & apply min
## on data | apply min on 'Confirmed' as 'Min Confirmed' 
data.agg(min('Confirmed').alias('Min Confirmed')) 

# on & show
## on data | show 
data.show() 

# on & sort_by desc
## on data | sort by 'Confirmed' descending 
data.sort(['Confirmed'], ascending=[False]) 

# on & select_rows
## on data | select rows 'SNo' > 100 
data.filter('SNo' > 100) 

# on & sort_by asc
## on data | sort by 'Confirmed' ascending 
data.sort(['Confirmed'], ascending=[True]) 

# on & describe
## on data | describe 
data.describe() 

# on & count
## on data | count 
data.count() 

# on & drop_duplicates
## on data | drop duplicates 
data.dropDuplicates() 

# on & union
## on data | union only_country_deaths 
data.unionByName(only_country_deaths) 

