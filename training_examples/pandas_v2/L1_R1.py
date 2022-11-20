# Target
## target code = pandas 
import pandas as pd

# load_from
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pd.read_csv('covid_19_data.csv') 

# create_dataframe
## only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths'
only_country_deaths = pd.DataFrame(data, columns=['Country/Region', 'Deaths']) 

# on & select_columns
## on data | select columns 'SNo', 'ObservationDate'
data[['SNo', 'ObservationDate']] 

# on & save_to csv
## on data | save to 'output.csv' as csv
data.to_csv('output.csv') 

# on & save_to json
## on data | save to 'output.json' as json
data.to_json('output.json') 

# on & difference
## on data | difference only_country_deaths
data[~data.isin(only_country_deaths).all(1)] 

# on & group_by
## on data | group by 'Country/Region'
data.groupby(['Country/Region']) 

# on & apply mean
## on data | apply mean on 'Confirmed' as 'Mean Confirmed'
data.agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean Confirmed'}) 

# on & append_column
## on data | append column 'Confirmed' - 'Recovered' as 'Deaths' 
data.assign(**{'Deaths': data.apply(lambda row: 'Confirmed' - 'Recovered', axis=1).values}) 

# on & apply sum
## on data | apply sum on 'Confirmed' as 'Total Confirmed' 
data.agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total Confirmed'}) 

# on & head
## on data | head 10 
data.head(10) 

# on & join right
## on data | join right only_country_deaths on 'Country/Region'
data.join(only_country_deaths, on=['Country/Region'], how='right') 

# on & drop_columns
## on data | drop columns 'Confirmed'
data.drop(columns=['Confirmed']) 

# on & replace_values
## on data | replace 'Confirmed' with 'Deaths'
data.replace('Confirmed', 'Deaths') 

# on & rename_columns
## on data | rename columns 'Confirmed' to 'Deaths' 
data.rename(columns={'Confirmed': 'Deaths'}) 

# on & intersection
## on data | intersection only_country_deaths 
data.merge(only_country_deaths) 

# on & show_schema
## on data | show schema 
data.info(verbose=False) 

# on & apply max
## on data | apply max on 'Confirmed' as 'Max Confirmed' 
data.agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max Confirmed'}) 

# on & join inner
## on data | join inner only_country_deaths on 'Country/Region' 
data.join(only_country_deaths, on=['Country/Region'], how='inner') 

# on & apply min
## on data | apply min on 'Confirmed' as 'Min Confirmed' 
data.agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min Confirmed'}) 

# on & show
## on data | show 
print(data) 

# on & sort_by desc
## on data | sort by 'Confirmed' descending 
data.sort_values(['Confirmed'], axis='index', ascending=[False]) 

# on & select_rows
## on data | select rows 'SNo' > 100 
data['SNo' > 100] 

# on & sort_by asc
## on data | sort by 'Confirmed' ascending 
data.sort_values(['Confirmed'], axis='index', ascending=[True]) 

# on & describe
## on data | describe 
data.describe() 

# on & count
## on data | count 
data.shape[0] 

# on & drop_duplicates
## on data | drop duplicates 
data.drop_duplicates() 

# on & union
## on data | union only_country_deaths 
pd.concat([data, only_country_deaths]) 

