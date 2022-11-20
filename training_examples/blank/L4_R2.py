# on & select_columns & apply mean & group_by & save_to json
## on data | select columns 'SNo', 'ObservationDate' | apply mean on 'Confirmed' as 'Mean Confirmed' | group by 'Country/Region' | save to 'output.json' as json 

# load_from & head & apply min & show
## load from 'covid_19_data.csv' as csv_with_header | head 10 | apply min on 'Confirmed' as 'Min Confirmed' | show 

# on & union & drop_duplicates & join right & show_schema
## on data | union only_country_deaths | drop duplicates | join right only_country_deaths on 'Country/Region' | show schema 

# on & difference & replace_values & apply mean & rename_columns
## on data | difference only_country_deaths | replace 'Confirmed' with 'Deaths' | apply mean on 'Confirmed' as 'Mean Confirmed' | rename columns 'Confirmed' to 'Deaths' 

# on & sort_by desc & join inner & apply sum & save_to csv
## on data | sort by 'Confirmed' descending | join inner only_country_deaths on 'Country/Region' | apply sum on 'Confirmed' as 'Total Confirmed' | save to 'output.csv' as csv 

# on & append_column & rename_columns & replace_values & intersection
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' | rename columns 'Confirmed' to 'Deaths' | replace 'Confirmed' with 'Deaths' | intersection only_country_deaths 

# create_dataframe & apply sum & drop_columns & save_to csv
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' | drop columns 'Confirmed' | save to 'output.csv' as csv 

# on & join right & append_column & count & show
## on data | join right only_country_deaths on 'Country/Region' | append column 'Confirmed' - 'Recovered' as 'Deaths' | count | show

# on & group_by & sort_by asc & head & describe
## on data | group by 'Country/Region' | sort by 'Confirmed' ascending | head 10 | describe 

# on & join inner & select_rows & apply max & show_schema
## on data | join inner only_country_deaths on 'Country/Region' | select rows 'SNo' > 100 | apply max on 'Confirmed' as 'Max Confirmed' | show schema 

# load_from & intersection & sort_by asc & select_rows
## load from 'covid_19_data.csv' as csv_with_header | intersection only_country_deaths | sort by 'Confirmed' ascending | select rows 'SNo' > 100 

# create_dataframe & drop_columns & select_columns & describe
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | drop columns 'Confirmed' | select columns 'SNo', 'ObservationDate' | describe 

# on & apply max & apply min & union & save_to json
## on data | apply max on 'Confirmed' as 'Max Confirmed' | apply min on 'Confirmed' as 'Min Confirmed' | union only_country_deaths | save to 'output.json' as json 

# on & sort_by desc & drop_duplicates & difference & count
## on data | sort by 'Confirmed' descending | drop duplicates | difference only_country_deaths | count 

