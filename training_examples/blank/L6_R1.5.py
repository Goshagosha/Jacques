# on & drop_duplicates & difference & apply mean & select_columns & intersection & show_schema
## on data | drop duplicates | difference only_country_deaths | apply mean on 'Confirmed' as 'Mean Confirmed' | select columns 'SNo', 'ObservationDate' | intersection only_country_deaths | show schema 

# on & sort_by asc & apply mean & apply sum & union & replace_values & count
## on data | sort by 'Confirmed' ascending | apply mean on 'Confirmed' as 'Mean Confirmed' | apply sum on 'Confirmed' as 'Total Confirmed' | union only_country_deaths | replace 'Confirmed' with 'Deaths' | count 

# on & sort_by asc & drop_columns & join inner & group_by & join right & save_to json
## on data | sort by 'Confirmed' ascending | drop columns 'Confirmed' | join inner only_country_deaths on 'Country/Region' | group by 'Country/Region' | join right only_country_deaths on 'Country/Region' | save to 'output.json' as json 

# load_from & rename_columns & apply max & head & intersection & save_to csv
## load from 'covid_19_data.csv' as csv_with_header | rename columns 'Confirmed' to 'Deaths' | apply max on 'Confirmed' as 'Max Confirmed' | head 10 | intersection only_country_deaths | save to 'output.csv' as csv 

# on & apply min & group_by & select_rows & apply max & append_column & save_to json
## on data | apply min on 'Confirmed' as 'Min Confirmed' | group by 'Country/Region' | select rows 'SNo' > 100 | apply max on 'Confirmed' as 'Max Confirmed' | append column 'Confirmed' - 'Recovered' as 'Deaths' | save to 'output.json' as json 

# create_dataframe & rename_columns & apply min & sort_by desc & describe & show
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | rename columns 'Confirmed' to 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' | sort by 'Confirmed' descending | describe | show 

# load_from & create_dataframe & join inner & replace_values & head & show_schema
## load from 'covid_19_data.csv' as csv_with_header | only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | join inner only_country_deaths on 'Country/Region' | replace 'Confirmed' with 'Deaths' | head 10 | show schema 

