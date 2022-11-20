# Target
## target code = pandas
import pandas as pd

# load_from & apply min
## data = load from 'covid_19_data.csv' as csv_with_header | apply min on 'Confirmed' as 'Min Confirmed' 
data = pd.read_csv('covid_19_data.csv').agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}) 

# create_dataframe & head
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | head 10 
only_country_deaths = pd.DataFrame(data, columns=['Country/Region', 'Deaths']).head(10) 

# on & intersection & sort_by desc
## on data | intersection only_country_deaths | sort by 'Confirmed' descending 
data.merge(only_country_deaths).sort_values(['Confirmed'], axis='index', ascending=[False]) 

# on & apply mean & replace_values
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | replace 'Confirmed' with 'Deaths'
data.agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'}).replace('Confirmed', 'Deaths') 

# on & select_columns & select_rows
## on data | select columns 'SNo', 'ObservationDate' | select rows 'SNo' > 100
data[['SNo', 'ObservationDate']]['SNo' > 100] 

# on & join inner & count
## on data | join inner only_country_deaths on 'Country/Region' | count
data.join(only_country_deaths, on=['Country/Region'], how='inner').shape[0] 

# on & union & save_to json
## on data | union only_country_deaths | save to 'output.json' as json
pd.concat([data, only_country_deaths]).to_json('output.json') 

# on & sort_by asc & show
## on data | sort by 'Confirmed' ascending | show 
print(data.sort_values(['Confirmed'], axis='index', ascending=[True])) 

# on & apply sum & show_schema
## on data | apply sum on 'Confirmed' as 'Total Confirmed' | show schema 
data.agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}).info(verbose=False) 

# on & group_by & save_to csv
## on data | group by 'Country/Region' | save to 'output.csv' as csv 
data.groupby(['Country/Region']).to_csv('output.csv') 

# on & drop_columns & describe
## on data | drop columns 'Confirmed' | describe 
data.drop(columns=['Confirmed']).describe() 

# on & join right & drop_duplicates
## on data | join right only_country_deaths on 'Country/Region' | drop duplicates 
data.join(only_country_deaths, on=['Country/Region'], how='right').drop_duplicates() 

# on & apply max & rename_columns
## on data | apply max on 'Confirmed' as 'Max Confirmed' | rename columns 'Confirmed' to 'Deaths' 
data.agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).rename(columns={'Confirmed': 'Deaths'}) 

# on & difference & append_column
## on data | difference only_country_deaths | append column 'Confirmed' - 'Recovered' as 'Deaths' 
data[~data.isin(only_country_deaths).all(1)].assign(**{'Deaths': data[~data.isin(only_country_deaths).all(1)].apply(lambda row: 'Confirmed' - 'Recovered', axis=1).values}) 

