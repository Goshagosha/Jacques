# Target
## target code = pandas
import pandas as pd

# load_from
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pd.read_csv('covid_19_data.csv') 

# create_dataframe & save_to csv
## df1 = create dataframe from data with header 'Country/Region' | save to 'save_target.csv' as csv 
df1 = pd.DataFrame(data, columns=['Country/Region']).to_csv('save_target.csv') 

# union & save_to json
## on data | union df1 | save to 'another_save.csv' as json 
pd.concat([data, df1]).to_json('another_save.csv') 

# group_by & union
## on data | group by 'Country/Region' | union df1 
pd.concat([data.groupby(['Country/Region']), df1]) 

# difference & intersection
## on data | difference df1 | intersection df2 
data[~data.isin(df1).all(1)].merge(df2) 

# select_columns & select_rows
## on data | select columns 'Country/Region', 'Confirmed', 'Deaths' | select rows 'Deaths' > 100 
data[['Country/Region', 'Confirmed', 'Deaths']]['Deaths' > 100] 

# drop_columns & join
## on data | drop columns 'Confirmed' | join left df1 on 'Deaths' 
data.drop(columns=['Confirmed']).join(df1, on=['Deaths'], how='left') 

# group_by & replace_values
## on data | group by 'Country/Region' | replace 'Mainland China' with 'China' 
data.groupby(['Country/Region']).replace('Mainland China', 'China') 

# apply min & replace_values
## on data | apply min on 'Deaths' as 'Minimal deaths' | replace 0 with 1 
data.agg({'Deaths' : 'min'}).rename(columns={'Deaths' : 'Minimal deaths'}).replace(0, 1) 

# difference & rename_columns
## on data | difference df1 | rename columns 'Deaths' to 'Departed' 
data[~data.isin(df1).all(1)].rename(columns={'Deaths': 'Departed'}) 

# rename_columns & show
## on data | rename columns 'Confirmed' to 'Sure' | show 
print(data.rename(columns={'Confirmed': 'Sure'})) 

# show_schema & describe
## on data | show schema | describe 
data.info(verbose=False).describe() 

# head & save_to json
## on data | head 100 | save to 'first_hundred.json' as json 
data.head(100).to_json('first_hundred.json') 

# select_columns & show
## on data | select columns 'Confirmed', 'Deaths' | show 
print(data[['Confirmed', 'Deaths']]) 

# append_column & sort_by ... ascending
## on data | append column 'Confirmed' - 'Deaths' as 'Survivors' | sort by 'Survivors' ascending 
data.assign(**{'Survivors': data.apply(lambda row: 'Confirmed' - 'Deaths', axis=1).values}).sort_values(['Survivors'], axis='index', ascending=[True]) 

# sort_by ... descending & drop_duplicates
## on data | sort by 'Deaths' descending | drop duplicates 
data.sort_values(['Deaths'], axis='index', ascending=[False]).drop_duplicates() 

# apply mean & sort_by ascending
## on data | apply mean on 'Deaths' as 'Mean deaths' | sort by 'Mean deaths' ascending 
data.agg({'Deaths' : 'mean'}).rename(columns={'Deaths' : 'Mean deaths'}).sort_values(['Mean deaths'], axis='index', ascending=[True]) 

# head & count
## on data | head 100 | count 
data.head(100).shape[0] 

# apply mean & apply max
## on data | apply mean on 'Deaths' as 'Mean deaths' | apply max on 'Confirmed' as 'Max confirmed' 
data.agg({'Deaths' : 'mean'}).rename(columns={'Deaths' : 'Mean deaths'}).agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Max confirmed'}) 

# apply min & apply sum
## on data | apply min on 'Confirmed' as 'Min confirmed' | apply sum on 'Deaths' as 'Totals deaths' 
data.agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min confirmed'}).agg({'Deaths' : 'sum'}).rename(columns={'Deaths' : 'Totals deaths'}) 

# apply sum & drop duplicates
## on data | apply sum on 'Confirmed' as 'Total confirmed' | drop duplicates 
data.agg({'Confirmed' : 'sum'}).rename(columns={'Confirmed' : 'Total confirmed'}).drop_duplicates() 
