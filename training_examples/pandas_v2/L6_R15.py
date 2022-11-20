# Target
## target code = pandas 
import pandas as pd

# necessity
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pd.read_csv('covid_19_data.csv') 

# necessity
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' 
only_country_deaths = pd.DataFrame(data, columns=['Country/Region', 'Deaths']) 

# on & drop_duplicates & difference & apply mean & select_columns & intersection & show_schema
## on data | drop duplicates | difference only_country_deaths | apply mean on 'Confirmed' as 'Mean Confirmed' | select columns 'SNo', 'ObservationDate' | intersection only_country_deaths | show schema 
data.drop_duplicates()[~data.drop_duplicates().isin(only_country_deaths).all(1)].agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'})[['SNo', 'ObservationDate']].merge(only_country_deaths).info(verbose=False) 

# on & sort_by asc & apply mean & apply sum & union & replace_values & count
## on data | sort by 'Confirmed' ascending | apply mean on 'Confirmed' as 'Mean Confirmed' | apply sum on 'Confirmed' as 'Total Confirmed' | union only_country_deaths | replace 'Confirmed' with 'Deaths' | count 
pd.concat([data.sort_values(['Confirmed'], axis='index', ascending=[True]).agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'}).agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}), only_country_deaths]).replace('Confirmed', 'Deaths').shape[0] 

# load_from & sort_by asc & drop_columns & join inner & group_by & join right & save_to json
## load from 'covid_19_data.csv' as csv_with_header | sort by 'Confirmed' ascending | drop columns 'Confirmed' | join inner only_country_deaths on 'Country/Region' | group by 'Country/Region' | join right only_country_deaths on 'Country/Region' | save to 'output.json' as json 
pd.read_csv('covid_19_data.csv').sort_values(['Confirmed'], axis='index', ascending=[True]).drop(columns=['Confirmed']).join(only_country_deaths, on=['Country/Region'], how='inner').groupby(['Country/Region']).join(only_country_deaths, on=['Country/Region'], how='right').to_json('output.json') 

# load_from & rename_columns & apply max & head & intersection & save_to csv
## load from 'covid_19_data.csv' as csv_with_header | rename columns 'Confirmed' to 'Deaths' | apply max on 'Confirmed' as 'Max Confirmed' | head 10 | intersection only_country_deaths | save to 'output.csv' as csv 
pd.read_csv('covid_19_data.csv').rename(columns={'Confirmed': 'Deaths'}).agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).head(10).merge(only_country_deaths).to_csv('output.csv') 

# on & apply min & group_by & select_rows & apply max & append_column & save_to json
## on data | apply min on 'Confirmed' as 'Min Confirmed' | group by 'Country/Region' | select rows 'SNo' > 100 | apply max on 'Confirmed' as 'Max Confirmed' | append column 'Confirmed' - 'Recovered' as 'Deaths' | save to 'output.json' as json 
data.agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}).groupby(['Country/Region'])['SNo' > 100].agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).assign(**{'Deaths': data.agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}).groupby(['Country/Region'])['SNo' > 100].agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).apply(lambda row: 'Confirmed' - 'Recovered', axis=1).values}).to_json('output.json') 

# create_dataframe & rename_columns & apply min & sort_by desc & describe & show
## create dataframe from data with header 'Country/Region', 'Deaths' | rename columns 'Confirmed' to 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' | sort by 'Confirmed' descending | describe | show 
print(pd.DataFrame(data, columns=['Country/Region', 'Deaths']).rename(columns={'Confirmed': 'Deaths'}).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}).sort_values(['Confirmed'], axis='index', ascending=[False]).describe()) 

# create_dataframe & join inner & replace_values & head & show_schema
## create dataframe from data with header 'Country/Region', 'Deaths' | join inner only_country_deaths on 'Country/Region' | replace 'Confirmed' with 'Deaths' | head 10 | show schema 
pd.DataFrame(data, columns=['Country/Region', 'Deaths']).join(only_country_deaths, on=['Country/Region'], how='inner').replace('Confirmed', 'Deaths').head(10).info(verbose=False) 

