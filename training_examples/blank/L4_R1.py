# load_from & sort_by desc & rename_columns & apply sum
## load from 'covid_19_data.csv' as csv_with_header | sort by 'Confirmed' descending | rename columns 'Confirmed' to 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' 

# necessity
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' 

# create_dataframe & group_by & join inner & count
## create dataframe from data with header 'Country/Region', 'Deaths' | group by 'Country/Region' | join inner only_country_deaths on 'Country/Region' | count 

# on & select_columns & head & sort_by asc & show
## on data | select columns 'SNo', 'ObservationDate' | head 10 | sort by 'Confirmed' ascending | show 

# on & replace_values & select_rows & intersection & describe
## on data | replace 'Confirmed' with 'Deaths' | select rows 'SNo' > 100 | intersection only_country_deaths | describe 

# on & difference & union & drop_columns & save_to json
## on data | difference only_country_deaths | union only_country_deaths | drop columns 'Confirmed' | save to 'output.json' as json 

# on & join right & apply max & drop_duplicates & show_schema
## on data | join right only_country_deaths on 'Country/Region' | apply max on 'Confirmed' as 'Max Confirmed' | drop duplicates | show schema 

# on & append_column & apply min & apply mean & save_to csv
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' | apply mean on 'Confirmed' as 'Mean Confirmed' | save to 'output.csv' as csv 

