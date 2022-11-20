# load_from & apply min
## data = load from 'covid_19_data.csv' as csv_with_header | apply min on 'Confirmed' as 'Min Confirmed' 

# create_dataframe & head
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | head 10 

# on & intersection & sort_by desc
## on data | intersection only_country_deaths | sort by 'Confirmed' descending 

# on & apply mean & replace_values
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | replace 'Confirmed' with 'Deaths' 

# on & select_columns & select_rows
## on data | select columns 'SNo', 'ObservationDate' | select rows 'SNo' > 100 

# on & join inner & count
## on data | join inner only_country_deaths on 'Country/Region' | count 

# on & union & save_to json
## on data | union only_country_deaths | save to 'output.json' as json 

# on & sort_by asc & show
## on data | sort by 'Confirmed' ascending | show 

# on & apply sum & show_schema
## on data | apply sum on 'Confirmed' as 'Total Confirmed' | show schema 

# on & group_by & save_to csv
## on data | group by 'Country/Region' | save to 'output.csv' as csv 

# on & drop_columns & describe
## on data | drop columns 'Confirmed' | describe 

# on & join right & drop_duplicates
## on data | join right only_country_deaths on 'Country/Region' | drop duplicates 

# on & apply max & rename_columns
## on data | apply max on 'Confirmed' as 'Max Confirmed' | rename columns 'Confirmed' to 'Deaths' 

# on & difference & append_column
## on data | difference only_country_deaths | append column 'Confirmed' - 'Recovered' as 'Deaths' 

