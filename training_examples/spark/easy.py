# Target
## target code = spark 
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("Spark Example").getOrCreate()


# load_from
## data = load from 'covid_19_data.csv' as csv_with_header 
data = spark.read.format('csv').option("header", True).load('covid_19_data.csv') 

# create_dataframe & save_to csv
## df1 = create dataframe from data with header 'Country/Region' | save to 'save_target.csv' as csv 
df1 = spark.createDataFrame(data, schema=['Country/Region']).write.format('csv').save('save_target.csv') 

# union & save_to json
## on data | union df1 | save to 'another_save.csv' as json 
data.unionByName(df1).write.format('json').save('another_save.csv') 

# group_by & union
## on data | group by 'Country/Region' | union df1 
data.groupBy(['Country/Region']).unionByName(df1) 

# difference & intersection
## on data | difference df1 | intersection df2 
data.subtract(df1).intersect(df2) 

# select_columns & select_rows
## on data | select columns 'Country/Region', 'Confirmed', 'Deaths' | select rows 'Deaths' > 100 
data.select(['Country/Region', 'Confirmed', 'Deaths']).filter('Deaths' > 100) 

# drop_columns & join
## on data | drop columns 'Confirmed' | join left df1 on 'Deaths' 
data.drop(['Confirmed']).join(df1, on=['Deaths'], how='left') 

# group_by & replace_values
## on data | group by 'Country/Region' | replace 'Mainland China' with 'China' 
data.groupBy(['Country/Region']).replace('Mainland China', 'China') 

# apply min & replace_values
## on data | apply min on 'Deaths' as 'Minimal deaths' | replace 0 with 1 
data.agg(min('Deaths').alias('Minimal deaths')).replace(0, 1) 

# difference & rename_columns
## on data | difference df1 | rename columns 'Deaths' to 'Departed' 
data.subtract(df1).withColumnRenamed('Deaths', 'Departed') 

# rename_columns & show
## on data | rename columns 'Confirmed' to 'Sure' | show 
data.withColumnRenamed('Confirmed', 'Sure').show() 

# show_schema & describe
## on data | show schema | describe 
data.printSchema().describe() 

# head & save_to json
## on data | head 100 | save to 'first_hundred.json' as json 
data.head(100).write.format('json').save('first_hundred.json') 

# select_columns & show
## on data | select columns 'Confirmed', 'Deaths' | show 
data.select(['Confirmed', 'Deaths']).show() 

# append_column & sort_by ... ascending
## on data | append column 'Confirmed' - 'Deaths' as 'Survivors' | sort by 'Survivors' ascending 
data.withColumn('Survivors', 'Confirmed' - 'Deaths').sort(['Survivors'], ascending=[True]) 

# sort_by ... descending & drop_duplicates
## on data | sort by 'Deaths' descending | drop duplicates 
data.sort(['Deaths'], ascending=[False]).dropDuplicates() 

# apply mean & sort_by ascending
## on data | apply mean on 'Deaths' as 'Mean deaths' | sort by 'Mean deaths' ascending 
data.agg(mean('Deaths').alias('Mean deaths')).sort(['Mean deaths'], ascending=[True]) 

# head & count
## on data | head 100 | count 
data.head(100).count() 

# apply mean & apply max
## on data | apply mean on 'Deaths' as 'Mean deaths' | apply max on 'Confirmed' as 'Max confirmed' 
data.agg(mean('Deaths').alias('Mean deaths')).agg(max('Confirmed').alias('Max confirmed')) 

# apply min & apply sum
## on data | apply min on 'Confirmed' as 'Min confirmed' | apply sum on 'Deaths' as 'Totals deaths' 
data.agg(min('Confirmed').alias('Min confirmed')).agg(sum('Deaths').alias('Totals deaths')) 

# apply sum & drop duplicates
## on data | apply sum on 'Confirmed' as 'Total confirmed' | drop duplicates 
data.agg(sum('Confirmed').alias('Total confirmed')).dropDuplicates() 
