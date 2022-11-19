# Target
## target code = polars
import polars as pl

# necessity
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pl.read_csv('covid_19_data.csv') 

# necessity
## only_country_deaths = create dataframe with header 'Country/Region', 'Deaths' 
only_country_deaths = pl.DataFrame({'Country/Region':[], 'Deaths':[]}) 

# on & drop_duplicates & apply mean & select_columns & show_schema
## on data | drop duplicates | apply mean on 'Confirmed' as 'Mean Confirmed' | select columns 'SNo', 'ObservationDate' | show schema 
print(data.unique().agg(pl.mean("Confirmed").alias("Mean Confirmed")).select[["SNo", "ObservationDate"]].schema)

# on & sort_by asc & apply mean & apply sum & union & replace_values & count
## on data | sort by 'Confirmed' ascending | apply mean on 'Confirmed' as 'Mean Confirmed' | apply sum on 'Confirmed' as 'Total Confirmed' | union only_country_deaths | replace 'Confirmed' with 'Deaths' | count 
pl.concat([data.sort("Confirmed").agg(pl.mean("Confirmed").alias("Mean Confirmed")).agg(pl.sum("Confirmed").alias("Total Confirmed")), only_country_deaths]).apply(lambda row: tuple(['Deaths' if x == 'Confirmed' else x for x in row])).shape[0]

# load_from & sort_by asc & drop_columns & join inner & group_by & join right & save_to json
## load from 'covid_19_data.csv' as csv_with_header | sort by 'Confirmed' ascending | drop columns 'Confirmed' | join inner only_country_deaths on 'Country/Region' | group by 'Country/Region' | join right only_country_deaths on 'Country/Region' | save to 'output.json' as json 
pl.read_csv('covid_19_data.csv').sort("Confirmed").drop("Confirmed").join(only_country_deaths, on="Country/Region", how="inner").groupby("Country/Region").join(only_country_deaths, on="Country/Region", how="right").write_json("output.json")

# load_from & rename_columns & apply max & head & save_to csv
## load from 'covid_19_data.csv' as csv_with_header | rename columns 'Confirmed' to 'Deaths' | apply max on 'Confirmed' as 'Max Confirmed' | head 10 | save to 'output.csv' as csv 
pl.read_csv('covid_19_data.csv').rename({'Confirmed': 'Deaths'}).agg(pl.max("Confirmed").alias("Max Confirmed")).head(10).write_csv("output.csv")

# on & apply min & group_by & select_rows & apply max & append_column & save_to json
## on data | apply min on 'Confirmed' as 'Min Confirmed' | group by 'Country/Region' | select rows 'SNo' > 100 | apply max on 'Confirmed' as 'Max Confirmed' | append column 'Confirmed' - 'Recovered' as 'Deaths' | save to 'output.json' as json 
data.agg(pl.min("Confirmed").alias("Min Confirmed")).groupby("Country/Region").filter(pl.col("SNo") > 100).agg(pl.max("Confirmed").alias("Max Confirmed")).with_column((pl.col("Confirmed") - pl.col("Recovered")).alias("Deaths")).write_json("output.json")

# create_dataframe & rename_columns & apply min & sort_by desc & describe & show
## create dataframe with header 'Country/Region', 'Deaths' | rename columns 'Confirmed' to 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' | sort by 'Confirmed' descending | describe | show 
print(pl.DataFrame({'Country/Region':[], 'Deaths':[]}).rename({'Confirmed': 'Deaths'}).agg(pl.min("Confirmed").alias("Min Confirmed")).sort("Confirmed", reverse=True).describe())

# create_dataframe & join inner & replace_values & head & show_schema
## create dataframe with header 'Country/Region', 'Deaths' | join inner only_country_deaths on 'Country/Region' | replace 'Confirmed' with 'Deaths' | head 10 | show schema 
print(pl.DataFrame({'Country/Region':[], 'Deaths':[]}).join(only_country_deaths, on="Country/Region", how="inner").apply(lambda row: tuple(['Deaths' if x == 'Confirmed' else x for x in row])).head(10).schema)

