# load_from & intersection & apply sum & show
## load from 'covid_19_data.csv' as csv_with_header | intersection only_country_deaths | apply sum on 'Confirmed' as 'Total Confirmed' | show 

# on & sort_by desc & apply min & difference & show
## on data | sort by 'Confirmed' descending | apply min on 'Confirmed' as 'Min Confirmed' | difference only_country_deaths | show 

# on & difference & apply max & select_columns & group_by
## on data | difference only_country_deaths | apply max on 'Confirmed' as 'Max Confirmed' | select columns 'SNo', 'ObservationDate' | group by 'Country/Region' 

# create_dataframe & join right & rename_columns & group_by
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | join right only_country_deaths on 'Country/Region' | rename columns 'Confirmed' to 'Deaths' | group by 'Country/Region' 

# on & apply max & apply mean & select_rows & count
## on data | apply max on 'Confirmed' as 'Max Confirmed' | apply mean on 'Confirmed' as 'Mean Confirmed' | select rows 'SNo' > 100 | count 

# on & head & replace_values & append_column & show_schema
## on data | head 10 | replace 'Confirmed' with 'Deaths' | append column 'Confirmed' - 'Recovered' as 'Deaths' | show schema 

# on & union & join inner & sort_by desc & save_to csv
## on data | union only_country_deaths | join inner only_country_deaths on 'Country/Region' | sort by 'Confirmed' descending | save to 'output.csv' as csv 

# on & rename_columns & intersection & apply sum & show_schema
## on data | rename columns 'Confirmed' to 'Deaths' | intersection only_country_deaths | apply sum on 'Confirmed' as 'Total Confirmed' | show schema 

# on & drop_columns & head & join right & count
## on data | drop columns 'Confirmed' | head 10 | join right only_country_deaths on 'Country/Region' | count 

# load_from & drop_duplicates & sort_by asc & save_to csv
## load from 'covid_19_data.csv' as csv_with_header | drop duplicates | sort by 'Confirmed' ascending | save to 'output.csv' as csv 

# on & describe & save_to json
## on data | describe | save to 'output.json' as json 

