# Target
## target code = pandas 
import pandas as pd

# necessity
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pd.read_csv('covid_19_data.csv') 

# necessity
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' 
only_country_deaths = pd.DataFrame(data, columns=['Country/Region', 'Deaths']) 

# on & select_columns & apply mean & group_by & save_to json
## on data | select columns 'SNo', 'ObservationDate' | apply mean on 'Confirmed' as 'Mean Confirmed' | group by 'Country/Region' | save to 'output.json' as json 
data[['SNo', 'ObservationDate']].agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'}).groupby(['Country/Region']).to_json('output.json') 

# load_from & head & apply min & show
## load from 'covid_19_data.csv' as csv_with_header | head 10 | apply min on 'Confirmed' as 'Min Confirmed' | show 
print(pd.read_csv('covid_19_data.csv').head(10).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'})) 

# on & union & drop_duplicates & join right & show_schema
## on data | union only_country_deaths | drop duplicates | join right only_country_deaths on 'Country/Region' | show schema 
pd.concat([data, only_country_deaths]).drop_duplicates().join(only_country_deaths, on=['Country/Region'], how='right').info(verbose=False) 

# on & difference & replace_values & apply mean & rename_columns
## on data | difference only_country_deaths | replace 'Confirmed' with 'Deaths' | apply mean on 'Confirmed' as 'Mean Confirmed' | rename columns 'Confirmed' to 'Deaths' 
data[~data.isin(only_country_deaths).all(1)].replace('Confirmed', 'Deaths').agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'}).rename(columns={'Confirmed': 'Deaths'}) 

# on & sort_by desc & join inner & apply sum & save_to csv
## on data | sort by 'Confirmed' descending | join inner only_country_deaths on 'Country/Region' | apply sum on 'Confirmed' as 'Total Confirmed' | save to 'output.csv' as csv 
data.sort_values(['Confirmed'], axis='index', ascending=[False]).join(only_country_deaths, on=['Country/Region'], how='inner').agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}).to_csv('output.csv') 

# on & append_column & rename_columns & replace_values & intersection
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' | rename columns 'Confirmed' to 'Deaths' | replace 'Confirmed' with 'Deaths' | intersection only_country_deaths 
data.assign(**{'Deaths': data.apply(lambda row: 'Confirmed' - 'Recovered', axis=1).values}).rename(columns={'Confirmed': 'Deaths'}).replace('Confirmed', 'Deaths').merge(only_country_deaths) 

# create_dataframe & apply sum & drop_columns & save_to csv
## create dataframe from data with header 'Country/Region', 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' | drop columns 'Confirmed' | save to 'output.csv' as csv 
pd.DataFrame(data, columns=['Country/Region', 'Deaths']).agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}).drop(columns=['Confirmed']).to_csv('output.csv') 

# on & join right & append_column & count & show
## on data | join right only_country_deaths on 'Country/Region' | append column 'Confirmed' - 'Recovered' as 'Deaths' | count | show 
print(data.join(only_country_deaths, on=['Country/Region'], how='right').assign(**{'Deaths': data.join(only_country_deaths, on=['Country/Region'], how='right').apply(lambda row: 'Confirmed' - 'Recovered', axis=1).values}).shape[0]) 

# on & group_by & sort_by asc & head & describe
## on data | group by 'Country/Region' | sort by 'Confirmed' ascending | head 10 | describe 
data.groupby(['Country/Region']).sort_values(['Confirmed'], axis='index', ascending=[True]).head(10).describe() 

# on & join inner & select_rows & apply max & show_schema
## on data | join inner only_country_deaths on 'Country/Region' | select rows 'SNo' > 100 | apply max on 'Confirmed' as 'Max Confirmed' | show schema 
data.join(only_country_deaths, on=['Country/Region'], how='inner')['SNo' > 100].agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).info(verbose=False) 

# load_from & intersection & sort_by asc & select_rows
## load from 'covid_19_data.csv' as csv_with_header | intersection only_country_deaths | sort by 'Confirmed' ascending | select rows 'SNo' > 100 
pd.read_csv('covid_19_data.csv').merge(only_country_deaths).sort_values(['Confirmed'], axis='index', ascending=[True])['SNo' > 100] 

# create_dataframe & drop_columns & select_columns & describe
## create dataframe from data with header 'Country/Region', 'Deaths' | drop columns 'Confirmed' | select columns 'SNo', 'ObservationDate' | describe 
pd.DataFrame(data, columns=['Country/Region', 'Deaths']).drop(columns=['Confirmed'])[['SNo', 'ObservationDate']].describe() 

# on & apply max & apply min & union & save_to json
## on data | apply max on 'Confirmed' as 'Max Confirmed' | apply min on 'Confirmed' as 'Min Confirmed' | union only_country_deaths | save to 'output.json' as json 
pd.concat([data.agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}), only_country_deaths]).to_json('output.json') 

# on & sort_by desc & drop_duplicates & difference & count
## on data | sort by 'Confirmed' descending | drop duplicates | difference only_country_deaths | count 
data.sort_values(['Confirmed'], axis='index', ascending=[False]).drop_duplicates()[~data.sort_values(['Confirmed'], axis='index', ascending=[False]).drop_duplicates().isin(only_country_deaths).all(1)].shape[0] 

