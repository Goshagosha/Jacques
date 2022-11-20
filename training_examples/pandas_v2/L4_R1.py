# Target
## target code = pandas
import pandas as pd

# load_from & sort_by desc & rename_columns & apply sum
## data = load from 'covid_19_data.csv' as csv_with_header | sort by 'Confirmed' descending | rename columns 'Confirmed' to 'Deaths' | apply sum on 'Confirmed' as 'Total Confirmed' 
data = pd.read_csv('covid_19_data.csv').sort_values(['Confirmed'], axis='index', ascending=[False]).rename(columns={'Confirmed': 'Deaths'}).agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}) 

# necessity
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths' 
only_country_deaths = pd.DataFrame(data, columns=['Country/Region', 'Deaths']) 

# create_dataframe & group_by & join inner & count
## create dataframe from data with header 'Country/Region', 'Deaths' | group by 'Country/Region' | join inner only_country_deaths on 'Country/Region' | count 
pd.DataFrame(data, columns=['Country/Region', 'Deaths']).groupby(['Country/Region']).join(only_country_deaths, on=['Country/Region'], how='inner').shape[0] 

# on & select_columns & head & sort_by asc & show
## on data | select columns 'SNo', 'ObservationDate' | head 10 | sort by 'Confirmed' ascending | show 
print(data[['SNo', 'ObservationDate']].head(10).sort_values(['Confirmed'], axis='index', ascending=[True])) 

# on & replace_values & select_rows & intersection & describe
## on data | replace 'Confirmed' with 'Deaths' | select rows 'SNo' > 100 | intersection only_country_deaths | describe 
data.replace('Confirmed', 'Deaths')['SNo' > 100].merge(only_country_deaths).describe() 

# on & difference & union & drop_columns & save_to json
## on data | difference only_country_deaths | union only_country_deaths | drop columns 'Confirmed' | save to 'output.json' as json 
pd.concat([data[~data.isin(only_country_deaths).all(1)], only_country_deaths]).drop(columns=['Confirmed']).to_json('output.json') 

# on & join right & apply max & drop_duplicates & show_schema
## on data | join right only_country_deaths on 'Country/Region' | apply max on 'Confirmed' as 'Max Confirmed' | drop duplicates | show schema 
data.join(only_country_deaths, on=['Country/Region'], how='right').agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}).drop_duplicates().info(verbose=False) 

# on & append_column & apply min & apply mean & save_to csv
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' | apply min on 'Confirmed' as 'Min Confirmed' | apply mean on 'Confirmed' as 'Mean Confirmed' | save to 'output.csv' as csv 
data.assign(**{'Deaths': data.apply(lambda row: 'Confirmed' - 'Recovered', axis=1).values}).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}).agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'}).to_csv('output.csv') 

