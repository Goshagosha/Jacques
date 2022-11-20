# Target
## target code = pandas
import pandas as pd

# load_from & save_to csv
## data = load from 'covid_19_data.csv' as csv_with_header | save to 'output.csv' as csv 
data = pd.read_csv('covid_19_data.csv').to_csv('output.csv') 

# create_dataframe & apply min
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' 
only_country_deaths = pd.DataFrame(data, columns=['Country/Region', 'Deaths']).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}) 

# on & sort_by desc & select_columns
## on data | sort by 'Confirmed' descending | select columns 'SNo', 'ObservationDate' 
data.sort_values(['Confirmed'], axis='index', ascending=[False])[['SNo', 'ObservationDate']] 

# on & difference & union
## on data | difference only_country_deaths | union only_country_deaths 
pd.concat([data[~data.isin(only_country_deaths).all(1)], only_country_deaths]) 

# on & rename_columns & drop_columns
## on data | rename columns 'Confirmed' to 'Deaths' | drop columns 'Confirmed' 
data.rename(columns={'Confirmed': 'Deaths'}).drop(columns=['Confirmed']) 

# on & head & apply max
## on data | head 10 | apply max on 'Confirmed' as 'Max Confirmed' 
data.head(10).agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}) 

# on & apply mean & save_to json
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | save to 'output.json' as json 
data.agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'}).to_json('output.json') 

# on & drop_duplicates & select_columns
## on data | drop duplicates | select columns 'SNo', 'ObservationDate' 
data.drop_duplicates()[['SNo', 'ObservationDate']] 

# on & sort_by asc & join inner
## on data | sort by 'Confirmed' ascending | join inner only_country_deaths on 'Country/Region' 
data.sort_values(['Confirmed'], axis='index', ascending=[True]).join(only_country_deaths, on=['Country/Region'], how='inner') 

# on & intersection & save_to json
## on data | intersection only_country_deaths | save to 'output.json' as json 
data.merge(only_country_deaths).to_json('output.json') 

# on & append_column & show_schema
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' | show schema 
data.assign(**{'Deaths': data.apply(lambda row: 'Confirmed' - 'Recovered', axis=1).values}).info(verbose=False) 

# on & replace_values & drop_columns
## on data | replace 'Confirmed' with 'Deaths' | drop columns 'Confirmed' 
data.replace('Confirmed', 'Deaths').drop(columns=['Confirmed']) 

# on & apply mean & save_to csv
## on data | apply mean on 'Confirmed' as 'Mean Confirmed' | save to 'output.csv' as csv 
data.agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'}).to_csv('output.csv') 

# on & drop_duplicates & apply min
## on data | drop duplicates | apply min on 'Confirmed' as 'Min Confirmed'
data.drop_duplicates().agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}) 

# on & join right & show
## on data | join right only_country_deaths on 'Country/Region' | show 
print(data.join(only_country_deaths, on=['Country/Region'], how='right')) 

# on & sort_by asc & apply sum
## on data | sort by 'Confirmed' ascending | apply sum on 'Confirmed' as 'Total Confirmed' 
data.sort_values(['Confirmed'], axis='index', ascending=[True]).agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}) 

# on & replace_values & describe
## on data | replace 'Confirmed' with 'Deaths' | describe 
data.replace('Confirmed', 'Deaths').describe() 

# on & select_rows & describe
## on data | select rows 'SNo' > 100 | describe 
data['SNo' > 100].describe() 

# on & difference & rename_columns
## on data | difference only_country_deaths | rename columns 'Confirmed' to 'Deaths' 
data[~data.isin(only_country_deaths).all(1)].rename(columns={'Confirmed': 'Deaths'}) 

# on & apply max & count
## on data | apply max on 'Confirmed' as 'Max Confirmed' | count 
data.agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).shape[0] 

# load_from & union
## load from 'covid_19_data.csv' as csv_with_header | union only_country_deaths 
pd.concat([pd.read_csv('covid_19_data.csv'), only_country_deaths]) 

# on & select_rows & intersection
## on data | select rows 'SNo' > 100 | intersection only_country_deaths 
data['SNo' > 100].merge(only_country_deaths) 

# on & count & show
## on data | count | show 
print(data.shape[0]) 

# create_dataframe & append_column
## create dataframe from data with header 'Country/Region', 'Deaths' | append column 'Confirmed' - 'Recovered' as 'Deaths' 
pd.DataFrame(data, columns=['Country/Region', 'Deaths']).assign(**{'Deaths': pd.DataFrame(data, columns=['Country/Region', 'Deaths']).apply(lambda row: 'Confirmed' - 'Recovered', axis=1).values}) 

# on & apply sum & group_by
## on data | apply sum on 'Confirmed' as 'Total Confirmed' | group by 'Country/Region' 
data.agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}).groupby(['Country/Region']) 

# on & join right & head
## on data | join right only_country_deaths on 'Country/Region' | head 10 
data.join(only_country_deaths, on=['Country/Region'], how='right').head(10) 

# on & sort_by desc & join inner
## on data | sort by 'Confirmed' descending | join inner only_country_deaths on 'Country/Region' 
data.sort_values(['Confirmed'], axis='index', ascending=[False]).join(only_country_deaths, on=['Country/Region'], how='inner') 

# on & group_by & show_schema
## on data | group by 'Country/Region' | show schema 
data.groupby(['Country/Region']).info(verbose=False) 

