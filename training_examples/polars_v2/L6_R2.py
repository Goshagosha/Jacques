# Target
## target code = polars
import polars as pl

# necessity
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pl.read_csv('covid_19_data.csv') 

# necessity
## only_country_deaths = create dataframe with header 'Country/Region', 'Deaths' 
only_country_deaths = pl.DataFrame({'Country/Region':[], 'Deaths':[]}) 

# load_from & join right & head & rename_columns & apply min & count
## load from 'covid_19_data.csv' as csv_with_header | join right only_country_deaths on 'Country/Region' | head 10 | rename columns 'Confirmed' to 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' | count 
pl.read_csv('covid_19_data.csv').join(only_country_deaths, on="Country/Region", how="right").head(10).rename({'Confirmed': 'Deaths'}).agg(pl.min("Confirmed").alias("Min Confirmed")).shape[0]

# load_from & apply min & sort_by asc & apply mean & show_schema
## load from 'covid_19_data.csv' as csv_with_header | apply min on 'Confirmed' as 'Min Confirmed' | sort by 'Confirmed' ascending | apply mean on 'Confirmed' as 'Mean Confirmed' | show schema 
print(pl.read_csv('covid_19_data.csv').agg(pl.min("Confirmed").alias("Min Confirmed")).sort("Confirmed", reverse=False).agg(pl.mean("Confirmed").alias("Mean Confirmed")).schema)

# on & apply sum & head & append_column & apply mean & count & show 
## on data | apply sum on 'Confirmed' as 'Total Confirmed' | head 10 | append column 'Confirmed' - 'Recovered' as 'Deaths' | apply mean on 'Confirmed' as 'Mean Confirmed' | count | show 
print(data.agg(pl.sum("Confirmed").alias("Total Confirmed")).head(10).with_column((pl.col("Confirmed") - pl.col("Recovered")).alias("Deaths")).agg(pl.mean("Confirmed").alias("Mean Confirmed")).shape[0])

# on & group_by & rename_columns & sort_by desc & select_rows & select_columns & describe
## on data | group by 'Country/Region' | rename columns 'Confirmed' to 'Deaths' | sort by 'Confirmed' descending | select rows 'SNo' > 100 | select columns 'SNo', 'ObservationDate' | describe 
data.groupby("Country/Region").rename({'Confirmed': 'Deaths'}).sort("Confirmed", reverse=True).filter(pl.col("SNo") > 100).select[["SNo", "ObservationDate"]].describe()

# on & drop_columns & apply max & append_column & join inner & replace_values & show_schema
## on data | drop columns 'Confirmed' | apply max on 'Confirmed' as 'Max Confirmed' | append column 'Confirmed' - 'Recovered' as 'Deaths' | join inner only_country_deaths on 'Country/Region' | replace 'Confirmed' with 'Deaths' | show schema 
print(data.drop("Confirmed").agg(pl.max("Confirmed").alias("Max Confirmed")).with_column((pl.col("Confirmed") - pl.col("Recovered")).alias("Deaths")).join(only_country_deaths, on="Country/Region", how="inner").apply(lambda row: tuple(['Deaths' if x == 'Confirmed' else x for x in row])).schema)

# on & apply max & group_by & sort_by asc & drop_columns & describe
## on data | apply max on 'Confirmed' as 'Max Confirmed' | group by 'Country/Region' | sort by 'Confirmed' ascending | drop columns 'Confirmed' | describe 
data.agg(pl.max("Confirmed").alias("Max Confirmed")).groupby("Country/Region").sort("Confirmed", reverse=False).drop("Confirmed").describe()

# on & join inner & drop_duplicates & join right & union & select_columns & show 
## on data | join inner only_country_deaths on 'Country/Region' | drop duplicates | join right only_country_deaths on 'Country/Region' | union only_country_deaths | select columns 'SNo', 'ObservationDate' | show 
print(data.join(only_country_deaths, on="Country/Region", how="inner").unique().join(only_country_deaths, on="Country/Region", how="right").union(only_country_deaths).select[["SNo", "ObservationDate"]])

# create_dataframe & replace_values & union & save_to csv
## create dataframe with header 'Country/Region', 'Deaths' | replace 'Confirmed' with 'Deaths' | union only_country_deaths | save to 'output.csv' as csv 
pl.concat([pl.DataFrame({'Country/Region':[], 'Deaths':[]}).apply(lambda row: tuple(['Deaths' if x == 'Confirmed' else x for x in row])), only_country_deaths]).to_csv('output.csv')

# create_dataframe & apply sum & drop_duplicates & select_rows & save_to json
## create dataframe with header 'Country/Region', 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' | drop duplicates | select rows 'SNo' > 100 | save to 'output.json' as json 
pl.DataFrame({'Country/Region':[], 'Deaths':[]}).agg(pl.sum("Confirmed").alias("Total Confirmed")).unique().filter(pl.col("SNo") > 100).to_json('output.json')

# on & sort_by desc & save_to json
## on data | sort by 'Confirmed' descending | save to 'output.json' as json 
data.sort("Confirmed", reverse=True).to_json('output.json')
