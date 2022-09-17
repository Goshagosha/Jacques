# Target
## target code = pandas
import pandas as pd

# load_from
## data = load from 'covid_19_data.csv' as csv_with_header
data = pd.read_csv("covid_19_data.csv")

# on_dataframe
## on data
data

# create_dataframe
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths'
only_country_deaths = pd.DataFrame(data, columns=["Country/Region", "Deaths"])

# save_to csv
## on data | save to 'output.csv' as csv
data.to_csv("output.csv")

# save_to json
## on data | save to 'output.json' as json
data.to_json("output.json")

# union
## united = on data | union only_country_deaths
united = pd.concat([data, only_country_deaths])

# difference
## differed = on data | difference only_country_deaths
differed = data[~data.isin(only_country_deaths).all(1)]

# intersection
## intersected = on data | intersection only_country_deaths
intersected = data.merge(only_country_deaths)

# select_columns
## on data | select columns 'SNo', 'ObservationDate'
data[["SNo", "ObservationDate"]]

# select_rows
## on data | select rows ('SNo' > 100) and ('SNo' < 200)
data[("SNo" > 100) & ("SNo" < 200)]

# drop_columns
## on data | drop columns 'Confirmed'
data.drop(columns=["Confirmed"])

# join
## on data | join inner only_country_deaths on 'Country/Region'
data.join(only_country_deaths, on=["Country/Region"], how="inner")

# group_by
## on data | group by 'Country/Region'
data.groupby(["Country/Region"])

# replace_values
## on data | replace 1 with 0
data.replace(1, 0)

# append_column
## on data | append column 0 as 'Empty'
data.assign(**{"Empty": data.apply(lambda row: 0, axis=1).values})

# sort_by
## on data | sort by 'Country/Region' ascending
data.sort_values(["Country/Region"], axis="index", ascending=[True])

# sort_by
## on data | sort by 'Country/Region' descending
data.sort_values(["Country/Region"], axis="index", ascending=[False])

# drop_duplicates
## on data | drop duplicates
data.drop_duplicates()

# rename_columns
## on data | rename columns 'Country/Region' to 'Country'
data.rename(columns={"Country/Region": "Country"})

# show
## on data | show
print(data)

# show_schema
## on data | show schema
data.info(verbose=False)

# describe
## on data | describe
data.describe()

# head
## on data | head 10
data.head(10)

# count
## on data | count
data.shape[0]

# apply
## on data | apply mean on 'Confirmed' as 'Mean Confirmed'
data.agg({"Confirmed": "mean"}).rename(columns={"Confirmed": "Mean Confirmed"})

# apply
## on data | apply sum on 'Confirmed' as 'Total Confirmed'
data.agg({"Confirmed": "sum"}).rename(columns={"Confirmed": "Total Confirmed"})

# apply
## on data | apply max on 'Confirmed' as 'Max Confrimed'
data.agg({"Confirmed": "max"}).rename(columns={"Confirmed": "Max Confrimed"})

# apply
## on data | apply min on 'Confirmed' as 'Min Confirmed'
data.agg({"Confirmed": "min"}).rename(columns={"Confirmed": "Min Confirmed"})
