# on & apply mean & apply max & drop_duplicates & difference & count & show
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | apply max on 'Confirmed' as 'Max Confirmed' | drop duplicates | difference only_country_deaths | count | show

# on & drop_columns & union & select_rows & select_columns & rename_columns & save_to json
## on data | drop columns 'Confirmed' | union only_country_deaths | select rows 'SNo' > 100 | select columns 'SNo', 'ObservationDate' | rename columns 'Confirmed' to 'Deaths' | save to 'output.json' as json 

# load_from & intersection & join inner & sort_by asc & apply min & describe
## load from 'covid_19_data.csv' as csv_with_header | intersection only_country_deaths | join inner only_country_deaths on 'Country/Region' | sort by 'Confirmed' ascending | apply min on 'Confirmed' as 'Min Confirmed' | describe 

# create_dataframe & apply sum & join right & head & replace_values & save_to csv
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' | join right only_country_deaths on 'Country/Region' | head 10 | replace 'Confirmed' with 'Deaths' | save to 'output.csv' as csv 

# on & group_by & append_column & sort_by desc & show_schema
## on data | group by 'Country/Region' | append column 'Confirmed' - 'Recovered' as 'Deaths' | sort by 'Confirmed' descending | show schema 

