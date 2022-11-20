# Target
## target code = polars
import polars as pl

# load_from
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pl.read_csv('covid_19_data.csv') 

# create_dataframe & save_to csv
## df1 = create dataframe with header 'Country/Region' | save to 'save_target.csv' as csv 
df1 = pl.DataFrame({'Country/Region':[]}).write_csv("save_target.csv") 

# union & save_to json
## on data | union df1 | save to 'another_save.json' as json 
pl.concat([data, df1]).write_json("another_save.json")

# group_by & union
## on data | group by 'Country/Region' apply mean on 'Confirmed' as 'Mean Confirmed' | union df1 
pl.concat([data.groupby("Country/Region").agg(pl.mean("Confirmed").alias("Mean Confirmed")), df1])

# select_columns & select_rows
## on data | select columns 'Country/Region', 'Confirmed', 'Deaths' | select rows 'Deaths' > 100 
data.select[["SNo", "ObservationDate"]].filter(pl.col("Deaths") > 100)

# drop_columns & join
## on data | drop columns 'Confirmed' | join left df1 on 'Deaths' 
data.drop("Confirmed").join(df1, on="Deaths", how="left")

# group_by & replace_values
## on data | group by 'Country/Region' apply min on 'Confirmed' as 'Min Confirmed' | replace 'Mainland China' with 'China' 
data.groupby("Country/Region").agg(pl.min("Confirmed").alias("Min Confirmed")).replace("Mainland China", "China").apply(lambda row: tuple(['China' if x == 'Mainland China' else x for x in row]))

# rename_columns & show
## on data | rename columns 'Confirmed' to 'Sure' | show 
print(data.rename({"Confirmed": "Sure"}))

!!!
# show_schema & describe
## on data | show schema | describe 

# head & save_to json
## on data | head 100 | save to 'first_hundred.json' as json 
data.head(100).write_json("first_hundred.json")

# select_columns & show
## on data | select columns 'Confirmed', 'Deaths' | show 
print(data.select[["Confirmed", "Deaths"]])

# append_column & sort_by ... ascending
# on data | append column 'Confirmed' - 'Deaths' as 'Survivors' | sort by 'Survivors' ascending 
## on data | append column 'Confirmed' - 'Deaths' as 'Survivors' | sort ascending by 'Survivors' 
data.with_column((pl.col("Confirmed") - pl.col("Deaths")).alias("Survivors")).sort("Survivors")

# sort_by ... descending & drop_duplicates
# on data | sort by 'Deaths' descending | drop duplicates 
## on data | sort descending by 'Deaths' | drop duplicates 
data.sort("Deaths", reverse=True).drop_duplicates()

!!!
# apply mean & sort_by ascending
# on data | apply mean on 'Deaths' as 'Mean deaths' | sort by 'Mean deaths' ascending 
## on data | apply mean on 'Deaths' as 'Mean deaths' | sort by ascending 'Mean deaths'

# head & count
## on data | head 100 | count 
data.head(100).shape[0]

# apply mean & apply max
## on data | apply mean on 'Deaths' as 'Mean deaths' | apply max on 'Confirmed' as 'Max confirmed' 

# apply min & apply sum
## on data | apply min on 'Confirmed' as 'Min confirmed' | apply sum on 'Deaths' as 'Totals deaths' 

# apply sum & drop duplicates
## on data | apply sum on 'Confirmed' as 'Total confirmed' | drop duplicates 
