# load_from & save_to csv
## data = load from 'covid_19_data.csv' as csv_with_header | save to 'output.csv' as csv 

# create_dataframe & apply min
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' 

# on & sort_by desc & select_columns
## on data | sort by 'Confirmed' descending | select columns 'SNo', 'ObservationDate' 

# on & difference & union
## on data | difference only_country_deaths | union only_country_deaths 

# on & rename_columns & drop_columns
## on data | rename columns 'Confirmed' to 'Deaths' | drop columns 'Confirmed' 

# on & head & apply max
## on data | head 10 | apply max on 'Confirmed' as 'Max Confirmed' 

# on & apply mean & save_to json
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | save to 'output.json' as json 

# on & drop_duplicates & select_columns
## on data | drop duplicates | select columns 'SNo', 'ObservationDate' 

# on & sort_by asc & join inner
## on data | sort by 'Confirmed' ascending | join inner only_country_deaths on 'Country/Region' 

# on & intersection & save_to json
## on data | intersection only_country_deaths | save to 'output.json' as json 

# on & append_column & show_schema
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' | show schema 

# on & replace_values & drop_columns
## on data | replace 'Confirmed' with 'Deaths' | drop columns 'Confirmed' 

# on & apply mean & save_to csv
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | save to 'output.csv' as csv 

# on & drop_duplicates & apply min
## on data | drop duplicates | apply min on 'Confirmed' as 'Min Confirmed' 

# on & join right & show
## on data | join right only_country_deaths on 'Country/Region' | show 

# on & sort_by asc & apply sum
## on data | sort by 'Confirmed' ascending | apply sum on 'Confirmed' as 'Total Confirmed' 

# on & replace_values & describe
## on data | replace 'Confirmed' with 'Deaths' | describe 

# on & select_rows & describe
## on data | select rows 'SNo' > 100 | describe 

# on & difference & rename_columns
## on data | difference only_country_deaths | rename columns 'Confirmed' to 'Deaths' 

# on & apply max & count
## on data | apply max on 'Confirmed' as 'Max Confirmed' | count 

# load_from & union
## load from 'covid_19_data.csv' as csv_with_header | union only_country_deaths 

# on & select_rows & intersection
## on data | select rows 'SNo' > 100 | intersection only_country_deaths 

# on & count & show
## on data | count | show 

# create_dataframe & append_column
## create dataframe from data with header 'Country/Region', 'Deaths' | append column 'Confirmed' - 'Recovered' as 'Deaths' 

# on & apply sum & group_by
## on data | apply sum on 'Confirmed' as 'Total Confirmed' | group by 'Country/Region' 

# on & join right & head
## on data | join right only_country_deaths on 'Country/Region' | head 10 

# on & sort_by desc & join inner
## on data | sort by 'Confirmed' descending | join inner only_country_deaths on 'Country/Region' 

# on & group_by & show_schema
## on data | group by 'Country/Region' | show schema 

