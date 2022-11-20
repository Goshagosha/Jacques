# load_from
## data = load from 'covid_19_data.csv' as csv_with_header 

# create_dataframe
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' 

# on & select_columns
## on data | select columns 'SNo', 'ObservationDate' 

# on & save_to csv
## on data | save to 'output.csv' as csv 

# on & save_to json
## on data | save to 'output.json' as json 

# on & difference
## on data | difference only_country_deaths 

# on & group_by
## on data | group by 'Country/Region' 

# on & apply mean
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' 

# on & append_column
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' 

# on & apply sum
## on data | apply sum on 'Confirmed' as 'Total Confirmed' 

# on & head
## on data | head 10 

# on & join right
## on data | join right only_country_deaths on 'Country/Region' 

# on & drop_columns
## on data | drop columns 'Confirmed' 

# on & replace_values
## on data | replace 'Confirmed' with 'Deaths' 

# on & rename_columns
## on data | rename columns 'Confirmed' to 'Deaths' 

# on & intersection
## on data | intersection only_country_deaths 

# on & show_schema
## on data | show schema 

# on & apply max
## on data | apply max on 'Confirmed' as 'Max Confirmed' 

# on & join inner
## on data | join inner only_country_deaths on 'Country/Region' 

# on & apply min
## on data | apply min on 'Confirmed' as 'Min Confirmed' 

# on & show
## on data | show 

# on & sort_by desc
## on data | sort by 'Confirmed' descending 

# on & select_rows
## on data | select rows 'SNo' > 100 

# on & sort_by asc
## on data | sort by 'Confirmed' ascending 

# on & describe
## on data | describe 

# on & count
## on data | count 

# on & drop_duplicates
## on data | drop duplicates 

# on & union
## on data | union only_country_deaths 

