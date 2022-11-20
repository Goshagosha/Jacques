# load_from & join right & head & rename_columns & apply min & count
## load from 'covid_19_data.csv' as csv_with_header | join right only_country_deaths on 'Country/Region' | head 10 | rename columns 'Confirmed' to 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' | count 

# load_from & apply min & difference & sort_by asc & apply mean & show_schema
## load from 'covid_19_data.csv' as csv_with_header | apply min on 'Confirmed' as 'Min Confirmed' | difference only_country_deaths | sort by 'Confirmed' ascending | apply mean on 'Confirmed' as 'Mean Confirmed' | show schema 

# on & apply sum & head & append_column & apply mean & count & show 
## on data | apply sum on 'Confirmed' as 'Total Confirmed' | head 10 | append column 'Confirmed' - 'Recovered' as 'Deaths' | apply mean on 'Confirmed' as 'Mean Confirmed' | count | show

# on & group_by & rename_columns & sort_by desc & select_rows & select_columns & describe
## on data | group by 'Country/Region' | rename columns 'Confirmed' to 'Deaths' | sort by 'Confirmed' descending | select rows 'SNo' > 100 | select columns 'SNo', 'ObservationDate' | describe 

# on & drop_columns & apply max & append_column & join inner & replace_values & show_schema
## on data | drop columns 'Confirmed' | apply max on 'Confirmed' as 'Max Confirmed' | append column 'Confirmed' - 'Recovered' as 'Deaths' | join inner only_country_deaths on 'Country/Region' | replace 'Confirmed' with 'Deaths' | show schema 

# on & apply max & group_by & sort_by asc & intersection & drop_columns & describe
## on data | apply max on 'Confirmed' as 'Max Confirmed' | group by 'Country/Region' | sort by 'Confirmed' ascending | intersection only_country_deaths | drop columns 'Confirmed' | describe 

# on & join inner & drop_duplicates & join right & union & select_columns & show 
## on data | join inner only_country_deaths on 'Country/Region' | drop duplicates | join right only_country_deaths on 'Country/Region' | union only_country_deaths | select columns 'SNo', 'ObservationDate' | show

# create_dataframe & intersection & replace_values & union & save_to csv
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | intersection only_country_deaths | replace 'Confirmed' with 'Deaths' | union only_country_deaths | save to 'output.csv' as csv

# create_dataframe & apply sum & drop_duplicates & select_rows & difference & save_to json
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' | drop duplicates | select rows 'SNo' > 100 | difference only_country_deaths | save to 'output.json' as json 

# on & sort_by desc & save_to json
## on data | sort by 'Confirmed' descending | save to 'output.json' as json 

