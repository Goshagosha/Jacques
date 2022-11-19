# Target
## target code = polars
import polars as pl

# load_from
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pl.read_csv('covid_19_data.csv') 

# on_dataframe
## on data 
data 

# create_dataframe 
## only_country_deaths = create dataframe with header 'Country/Region', 'Deaths' 
only_country_deaths = pl.DataFrame({'Country/Region':[], 'Deaths':[]}) 

# save_to csv
## on data | save to 'output.csv' as csv
data.write_csv("output.csv")

# save_to json
## on data | save to 'output.json' as json
data.write_json("output.json")

# union
## united = on data | union only_country_deaths
united = pl.concat([data, only_country_deaths])

# difference # NOT SUPPORTED

# intersection # NOT SUPPORTED

# select_columns
## on data | select columns 'SNo', 'ObservationDate'
data.select[["SNo", "ObservationDate"]]

# select_rows
## on data | select rows ('SNo' > 100)
data.filter(pl.col("SNo") > 100)

# drop_columns
## on data | drop columns 'Confirmed'
data.drop("Confirmed")

# join
## on data | join inner only_country_deaths on 'Country/Region'
data.join(only_country_deaths, on="Country/Region", how="inner")

# group_by
## on data | group by 'Country/Region' apply mean on 'Confirmed' as 'Mean Confirmed'
data.groupby("Country/Region").agg(pl.mean("Confirmed").alias("Mean Confirmed"))

# group_by
## on data | group by 'Country/Region' apply sum on 'Confirmed' as 'Total Confirmed'
data.groupby("Country/Region").agg(pl.sum("Confirmed").alias("Total Confirmed"))

# group_by
## on data | group by 'Country/Region' apply max on 'Confirmed' as 'Max Confirmed'
data.groupby("Country/Region").agg(pl.max("Confirmed").alias("Max Confirmed"))

# group_by
## on data | group by 'Country/Region' apply min on 'Confirmed' as 'Min Confirmed'
data.groupby("Country/Region").agg(pl.min("Confirmed").alias("Min Confirmed"))

# replace_values
## on data | replace 1 with 0
data.apply(lambda row: tuple([0 if x == 1 else x for x in row]))

# append_column
## on data | append column 0 as 'Empty'
data.with_column(pl.lit(0).alias("Empty"))

# sort_by
## on data | sort by 'Country/Region' ascending
data.sort("Country/Region")

# sort_by
## on data | sort by 'Country/Region' descending
data.sort("Country/Region", reverse=True)

# drop_duplicates
## on data | drop duplicates
data.unique()

# rename_columns
## on data | rename columns 'Country/Region' to 'Country'
data.rename({"Country/Region": "Country"})

# show
## on data | show
print(data)

# show_schema
## on data | show schema
print(data.schema)

# describe
## on data | describe
data.describe()

# head
## on data | head 10
data.head(10)

# count
## on data | count
data.shape[0]
