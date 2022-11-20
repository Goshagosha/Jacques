# Target
## target code = polars
import polars as pl

# necessity
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pl.read_csv('covid_19_data.csv') 

# necessity
## only_country_deaths = create dataframe with header 'Country/Region', 'Deaths' 
only_country_deaths = pl.DataFrame({'Country/Region':[], 'Deaths':[]}) 

# on & apply mean & apply max & drop_duplicates & count & show
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | apply max on 'Confirmed' as 'Max Confirmed' | drop duplicates | count | show 
print(data.agg(pl.mean("Confirmed").alias("Mean Confirmed")).agg(pl.max("Confirmed").alias("Max Confirmed")).unique().shape[0])

# on & drop_columns & union & select_rows & select_columns & rename_columns & save_to json
## on data | drop columns 'Confirmed' | union only_country_deaths | select rows 'SNo' > 100 | select columns 'SNo', 'ObservationDate' | rename columns 'Confirmed' to 'Deaths' | save to 'output.json' as json 
pl.concat([data.drop("Confirmed"), only_country_deaths]).filter(pl.col("SNo") > 100).select([["SNo", "ObservationDate"]]).rename({"Confirmed": "Deaths"}).write_json("output.json")

# load_from & join inner & sort_by asc & apply min & describe
## load from 'covid_19_data.csv' as csv_with_header | join inner only_country_deaths on 'Country/Region' | sort by 'Confirmed' ascending | apply min on 'Confirmed' as 'Min Confirmed' | describe 
pl.read_csv('covid_19_data.csv').join(only_country_deaths, on="Country/Region", how="inner").sort("Confirmed").agg(pl.min("Confirmed").alias("Min Confirmed")).describe()

# create_dataframe & apply sum & join right & head & replace_values & save_to csv
## create dataframe with header 'Country/Region', 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' | join right only_country_deaths on 'Country/Region' | head 10 | replace 'Confirmed' with 'Deaths' | save to 'output.csv' as csv 
pl.DataFrame({'Country/Region':[], 'Deaths':[]}).agg(pl.sum("Confirmed").alias("Total Confirmed")).join(only_country_deaths, on="Country/Region", how="right").head(10).apply(lambda row: tuple(['Deaths' if x == 'Confirmed' else x for x in row])).write_csv("output.csv")

# on & group_by & append_column & sort_by desc & show_schema
## on data | group by 'Country/Region' | append column 'Confirmed' - 'Recovered' as 'Deaths' | sort by 'Confirmed' descending | show schema 
print(data.groupby("Country/Region").with_column((pl.col("Confirmed") - pl.col("Recovered")).alias("Deaths")).sort("Confirmed", reverse=True).schema)
