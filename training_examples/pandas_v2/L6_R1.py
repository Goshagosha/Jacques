# Target
## target code = pandas 
import pandas as pd

# necessity
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pd.read_csv('covid_19_data.csv') 

# necessity
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' 
only_country_deaths = pd.DataFrame(data, columns=['Country/Region', 'Deaths']) 

# on & apply mean & apply max & drop_duplicates & difference & count & show
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | apply max on 'Confirmed' as 'Max Confirmed' | drop duplicates | difference only_country_deaths | count | show 
print(data.agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'}).agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).drop_duplicates()[~data.agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'}).agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).drop_duplicates().isin(only_country_deaths).all(1)].shape[0]) 

# on & drop_columns & union & select_rows & select_columns & rename_columns & save_to json
## on data | drop columns 'Confirmed' | union only_country_deaths | select rows 'SNo' > 100 | select columns 'SNo', 'ObservationDate' | rename columns 'Confirmed' to 'Deaths' | save to 'output.json' as json 
pd.concat([data.drop(columns=['Confirmed']), only_country_deaths])['SNo' > 100][['SNo', 'ObservationDate']].rename(columns={'Confirmed': 'Deaths'}).to_json('output.json') 

# load_from & intersection & join inner & sort_by asc & apply min & describe
## load from 'covid_19_data.csv' as csv_with_header | intersection only_country_deaths | join inner only_country_deaths on 'Country/Region' | sort by 'Confirmed' ascending | apply min on 'Confirmed' as 'Min Confirmed' | describe 
pd.read_csv('covid_19_data.csv').merge(only_country_deaths).join(only_country_deaths, on=['Country/Region'], how='inner').sort_values(['Confirmed'], axis='index', ascending=[True]).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}).describe() 

# create_dataframe & apply sum & join right & head & replace_values & save_to csv
## create dataframe from data with header 'Country/Region', 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' | join right only_country_deaths on 'Country/Region' | head 10 | replace 'Confirmed' with 'Deaths' | save to 'output.csv' as csv 
pd.DataFrame(data, columns=['Country/Region', 'Deaths']).agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}).join(only_country_deaths, on=['Country/Region'], how='right').head(10).replace('Confirmed', 'Deaths').to_csv('output.csv') 

# on & group_by & append_column & sort_by desc & show_schema
## on data | group by 'Country/Region' | append column 'Confirmed' - 'Recovered' as 'Deaths' | sort by 'Confirmed' descending | show schema 
data.groupby(['Country/Region']).assign(**{'Deaths': data.groupby(['Country/Region']).apply(lambda row: 'Confirmed' - 'Recovered', axis=1).values}).sort_values(['Confirmed'], axis='index', ascending=[False]).info(verbose=False) 

