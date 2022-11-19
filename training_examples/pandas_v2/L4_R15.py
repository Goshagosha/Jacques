# Target
## target code = pandas 
import pandas as pd

# necessity
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pd.read_csv('covid_19_data.csv') 

# necessity
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' 
only_country_deaths = pd.DataFrame(data, columns=['Country/Region', 'Deaths']) 

# load_from & intersection & apply sum & show
## load from 'covid_19_data.csv' as csv_with_header | intersection only_country_deaths | apply sum on 'Confirmed' as 'Total Confirmed' | show 
print(pd.read_csv('covid_19_data.csv').merge(only_country_deaths).agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'})) 

# on & sort_by desc & apply min & difference & show
## on data | sort by 'Confirmed' descending | apply min on 'Confirmed' as 'Min Confirmed' | difference only_country_deaths | show 
print(data.sort_values(['Confirmed'], axis='index', ascending=[False]).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'})[~data.sort_values(['Confirmed'], axis='index', ascending=[False]).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}).isin(only_country_deaths).all(1)]) 

# on & difference & apply max & select_columns & group_by
## on data | difference only_country_deaths | apply max on 'Confirmed' as 'Max Confirmed' | select columns 'SNo', 'ObservationDate' | group by 'Country/Region' 
data[~data.isin(only_country_deaths).all(1)].agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'})[['SNo', 'ObservationDate']].groupby(['Country/Region']) 

# create_dataframe & join right & rename_columns & group_by
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | join right only_country_deaths on 'Country/Region' | rename columns 'Confirmed' to 'Deaths' | group by 'Country/Region' 
only_country_deaths = pd.DataFrame(data, columns=['Country/Region', 'Deaths']).join(only_country_deaths, on=['Country/Region'], how='right').rename(columns={'Confirmed': 'Deaths'}).groupby(['Country/Region']) 

# on & apply max & apply mean & select_rows & count
## on data | apply max on 'Confirmed' as 'Max Confirmed' | apply mean on 'Confirmed' as 'Mean Confirmed' | select rows 'SNo' > 100 | count 
data.agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'})['SNo' > 100].shape[0] 

# on & head & replace_values & append_column & show_schema
## on data | head 10 | replace 'Confirmed' with 'Deaths' | append column 'Confirmed' - 'Recovered' as 'Deaths' | show schema 
data.head(10).replace('Confirmed', 'Deaths').assign(**{'Deaths': data.head(10).replace('Confirmed', 'Deaths').apply(lambda row: 'Confirmed' - 'Recovered', axis=1).values}).info(verbose=False) 

# on & union & join inner & sort_by desc & save_to csv
## on data | union only_country_deaths | join inner only_country_deaths on 'Country/Region' | sort by 'Confirmed' descending | save to 'output.csv' as csv 
pd.concat([data, only_country_deaths]).join(only_country_deaths, on=['Country/Region'], how='inner').sort_values(['Confirmed'], axis='index', ascending=[False]).to_csv('output.csv') 

# on & rename_columns & intersection & apply sum & show_schema
## on data | rename columns 'Confirmed' to 'Deaths' | intersection only_country_deaths | apply sum on 'Confirmed' as 'Total Confirmed' | show schema 
data.rename(columns={'Confirmed': 'Deaths'}).merge(only_country_deaths).agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}).info(verbose=False) 

# on & drop_columns & head & join right & count
## on data | drop columns 'Confirmed' | head 10 | join right only_country_deaths on 'Country/Region' | count 
data.drop(columns=['Confirmed']).head(10).join(only_country_deaths, on=['Country/Region'], how='right').shape[0] 

# load_from & drop_duplicates & sort_by asc & save_to csv
## load from 'covid_19_data.csv' as csv_with_header | drop duplicates | sort by 'Confirmed' ascending | save to 'output.csv' as csv 
pd.read_csv('covid_19_data.csv').drop_duplicates().sort_values(['Confirmed'], axis='index', ascending=[True]).to_csv('output.csv') 

# on & describe & save_to json
## on data | describe | save to 'output.json' as json 
data.describe().to_json('output.json') 

