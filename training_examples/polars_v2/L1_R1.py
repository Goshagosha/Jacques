## target code = polars
import polars as pl

# load_from
## data = load from 'covid_19_data.csv' as csv_with_header
data = pl.read_csv('covid_19_data.csv')

# create_dataframe
## only_country_deaths = create dataframe with header 'Country/Region', 'Deaths'
only_country_deaths = pl.DataFrame({'Country/Region':[], 'Deaths':[]}) 

# on & select_columns
## on data | select columns 'SNo', 'ObservationDate'
data.select[["SNo", "ObservationDate"]] 

# on & save_to csv
## on data | save to 'output.csv' as csv 
data.write_csv("output.csv")

# on & save_to json
## on data | save to 'output.json' as json 
data.write_json("output.json")

# on & group_by
## on data | group by 'Country/Region' 
data.groupby("Country/Region")

# on & apply mean
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' 
data.agg(pl.mean("Confirmed").alias("Mean Confirmed"))

# on & append_column
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' 
data.with_column((pl.col("Confirmed") - pl.col("Recovered")).alias("Deaths"))

# on & apply sum
## on data | apply sum on 'Confirmed' as 'Total Confirmed' 
data.agg(pl.sum("Confirmed").alias("Total Confirmed"))

# on & head
## on data | head 10 
data.head(10)

# on & join right
## on data | join right only_country_deaths on 'Country/Region' 
data.join(only_country_deaths, on="Country/Region", how="right")

# on & drop_columns
## on data | drop columns 'Confirmed' 
data.drop("Confirmed")

# on & replace_values
## on data | replace 'Confirmed' with 'Deaths' 
data.apply(lambda row: tuple(['Deaths' if x == 'Confirmed' else x for x in row]))

# on & rename_columns
## on data | rename columns 'Confirmed' to 'Deaths' 
data.rename({'Confirmed': 'Deaths'})

# on & show_schema
## on data | show schema 
print(data.schema)

# on & apply max
## on data | apply max on 'Confirmed' as 'Max Confirmed' 
data.agg(pl.max("Confirmed").alias("Max Confirmed"))

# on & join inner
## on data | join inner only_country_deaths on 'Country/Region' 
data.join(only_country_deaths, on="Country/Region", how="inner")

# on & apply min
## on data | apply min on 'Confirmed' as 'Min Confirmed' 
data.agg(pl.min("Confirmed").alias("Min Confirmed"))

# on & show
## on data | show 
print(data)

# on & sort_by desc
## on data | sort by 'Confirmed' descending 
data.sort("Confirmed", reverse=True)

# on & select_rows
## on data | select rows 'SNo' > 100 
data.filter(pl.col("SNo") > 100)

# on & sort_by asc
## on data | sort by 'Confirmed' ascending 
data.sort("Confirmed", reverse=False)

# on & describe
## on data | describe 
data.describe()

# on & count
## on data | count 
data.shape[0]

# on & drop_duplicates
## on data | drop duplicates 
data.unique()

# on & union
## on data | union only_country_deaths 
pl.concat([data, only_country_deaths])

