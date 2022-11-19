# Target
## target code = pandas 
import pandas as pd

# necessity
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pd.read_csv('covid_19_data.csv') 

# necessity
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' 
only_country_deaths = pd.DataFrame(data, columns=['Country/Region', 'Deaths']) 

# load_from & join right & head & rename_columns & apply min & count
## load from 'covid_19_data.csv' as csv_with_header | join right only_country_deaths on 'Country/Region' | head 10 | rename columns 'Confirmed' to 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' | count 
pd.read_csv('covid_19_data.csv').join(only_country_deaths, on=['Country/Region'], how='right').head(10).rename(columns={'Confirmed': 'Deaths'}).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}).shape[0] 

# load_from & apply min & difference & sort_by asc & apply mean & show_schema
## load from 'covid_19_data.csv' as csv_with_header | apply min on 'Confirmed' as 'Min Confirmed' | difference only_country_deaths | sort by 'Confirmed' ascending | apply mean on 'Confirmed' as 'Mean Confirmed' | show schema 
pd.read_csv('covid_19_data.csv').agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'})[~pd.read_csv('covid_19_data.csv').agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}).isin(only_country_deaths).all(1)].sort_values(['Confirmed'], axis='index', ascending=[True]).agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'}).info(verbose=False) 

# on & apply sum & head & append_column & apply mean & count & show 
## on data | apply sum on 'Confirmed' as 'Total Confirmed' | head 10 | append column 'Confirmed' - 'Recovered' as 'Deaths' | apply mean on 'Confirmed' as 'Mean Confirmed' | count | show 
print(data.agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}).head(10).assign(**{'Deaths': data.agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}).head(10).apply(lambda row: 'Confirmed' - 'Recovered', axis=1).values}).agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'}).shape[0]) 

# on & group_by & rename_columns & sort_by desc & select_rows & select_columns & describe
## on data | group by 'Country/Region' | rename columns 'Confirmed' to 'Deaths' | sort by 'Confirmed' descending | select rows 'SNo' > 100 | select columns 'SNo', 'ObservationDate' | describe 
data.groupby(['Country/Region']).rename(columns={'Confirmed': 'Deaths'}).sort_values(['Confirmed'], axis='index', ascending=[False])['SNo' > 100][['SNo', 'ObservationDate']].describe() 

# on & drop_columns & apply max & append_column & join inner & replace_values & show_schema
## on data | drop columns 'Confirmed' | apply max on 'Confirmed' as 'Max Confirmed' | append column 'Confirmed' - 'Recovered' as 'Deaths' | join inner only_country_deaths on 'Country/Region' | replace 'Confirmed' with 'Deaths' | show schema 
data.drop(columns=['Confirmed']).agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).assign(**{'Deaths': data.drop(columns=['Confirmed']).agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).apply(lambda row: 'Confirmed' - 'Recovered', axis=1).values}).join(only_country_deaths, on=['Country/Region'], how='inner').replace('Confirmed', 'Deaths').info(verbose=False) 

# on & apply max & group_by & sort_by asc & intersection & drop_columns & describe
## on data | apply max on 'Confirmed' as 'Max Confirmed' | group by 'Country/Region' | sort by 'Confirmed' ascending | intersection only_country_deaths | drop columns 'Confirmed' | describe 
data.agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).groupby(['Country/Region']).sort_values(['Confirmed'], axis='index', ascending=[True]).merge(only_country_deaths).drop(columns=['Confirmed']).describe() 

# on & join inner & drop_duplicates & join right & union & select_columns & show 
## on data | join inner only_country_deaths on 'Country/Region' | drop duplicates | join right only_country_deaths on 'Country/Region' | union only_country_deaths | select columns 'SNo', 'ObservationDate' | show 
print(pd.concat([data.join(only_country_deaths, on=['Country/Region'], how='inner').drop_duplicates().join(only_country_deaths, on=['Country/Region'], how='right'), only_country_deaths])[['SNo', 'ObservationDate']]) 

# create_dataframe & intersection & replace_values & union & save_to csv
## create dataframe from data with header 'Country/Region', 'Deaths' | intersection only_country_deaths | replace 'Confirmed' with 'Deaths' | union only_country_deaths | save to 'output.csv' as csv 
pd.concat([pd.DataFrame(data, columns=['Country/Region', 'Deaths']).merge(only_country_deaths).replace('Confirmed', 'Deaths'), only_country_deaths]).to_csv('output.csv') 

# create_dataframe & apply sum & drop_duplicates & select_rows & difference & save_to json
## create dataframe from data with header 'Country/Region', 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' | drop duplicates | select rows 'SNo' > 100 | difference only_country_deaths | save to 'output.json' as json 
pd.DataFrame(data, columns=['Country/Region', 'Deaths']).agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}).drop_duplicates()['SNo' > 100][~pd.DataFrame(data, columns=['Country/Region', 'Deaths']).agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}).drop_duplicates()['SNo' > 100].isin(only_country_deaths).all(1)].to_json('output.json') 

# on & sort_by desc & save_to json
## on data | sort by 'Confirmed' descending | save to 'output.json' as json 
data.sort_values(['Confirmed'], axis='index', ascending=[False]).to_json('output.json') 
