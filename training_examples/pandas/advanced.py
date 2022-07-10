# Target
## target code = pandas
import pandas as pd

# load_from
## data = load from 'covid_20_data.csv' as csv_with_header 
data = pd.read_csv('covid_20_data.csv') 

# create_dataframe & apply min & show_schema & sort_by ... descending
## other_df = create dataframe from data with header 'Country/Region', 'Confirmed' | apply min on 'Confirmed' as 'Min confirmed'| sort by 'Min confirmed' descending | show schema 
other_df = pd.DataFrame(data, columns=['Country/Region', 'Confirmed']).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Min confirmed'}).sort_values(['Min confirmed'], axis='index', ascending=[False]).info(verbose=False) 

# select_rows & select_columns & sort_by ... ascending & save_to csv
## on data | select rows 'Confirmed' > 100 | sort by 'Confirmed' ascending | save to 'save_target.csv' as csv 
data['Confirmed' > 100].sort_values(['Confirmed'], axis='index', ascending=[True]).to_csv('save_target.csv') 

# join & replace_values & append_column & apply sum
## on data | join left other_df on 'Confirmed' | append column 'Confirmed' - 'Deaths' as 'Active' | apply sum on 'Active' as 'Total Active' 
data.join(other_df, on=['Confirmed'], how='left').assign(**{'Active': data.join(other_df, on=['Confirmed'], how='left').apply(lambda row: 'Confirmed' - 'Deaths', axis=1).values}).agg({'Active' : 'sum'}).rename(columns={'Active' : 'Total Active'}) 

# intersection & difference & replace_values & show
## on data | intersection other_df | difference other_df | replace 0 with 'Unknown' | show 
print(data.merge(other_df)[~data.merge(other_df).isin(other_df).all(1)].replace(0, 'Unknown')) 

# union & head & apply mean & save_to csv
## on data | union other_df | head 150 | apply mean on 'Confirmed' as 'Mean confirmed' | save to 'training_examples/pandas/save_target.csv' as csv 
pd.concat([data, other_df]).head(150).agg({'Confirmed' : 'mean'}).rename(columns={'Confirmed' : 'Mean confirmed'}).to_csv('training_examples/pandas/save_target.csv') 

# select_columns & sort_by ... descending & head & apply mean
## on data | select columns 'Confirmed', 'Deaths', 'Active' | sort by 'Active' descending | head 250 | apply mean on 'Deaths' as 'Mean deaths of top 250' 
data[['Confirmed', 'Deaths', 'Active']].sort_values(['Active'], axis='index', ascending=[False]).head(250).agg({'Deaths' : 'mean'}).rename(columns={'Deaths' : 'Mean deaths of top 250'}) 

# apply max & apply max & drop_columns & save_to json
## on data | apply max on 'Active' as 'Top Active' | apply max on 'Deaths' as 'Most deaths' | drop columns 'Active', 'Deaths' | save to 'training_examples/pandas/save_target.csv' as json 
data.agg({'Active' : 'max'}).rename(columns={'Active' : 'Top Active'}).agg({'Deaths' : 'max'}).rename(columns={'Deaths' : 'Most deaths'}).drop(columns=['Active', 'Deaths']).to_json('training_examples/pandas/save_target.csv') 

# select_rows & join & group_by & show
## on data | select rows 'Active' > 200 | join right other_df on 'Active', 'Deaths' | group by 'Country/Region' | show 
print(data['Active' > 200].join(other_df, on=['Active', 'Deaths'], how='right').groupby(['Country/Region'])) 

# ~describe~ & apply sum & apply min & show_schema
## on data | apply sum on 'Active' as 'Total active' | apply min on 'Confirmed' as 'Least confirmed' | show schema 
data.agg({'Active' : 'sum'}).rename(columns={'Active' : 'Total active'}).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Least confirmed'}).info(verbose=False) 

# union & rename_columns & rename_columns & describe
## on data | rename columns 'Confirmed' to 'Confident', 'Active' to 'Still ill' | rename columns 'Deaths' to 'Departed' | describe 
data.rename(columns={'Confirmed': 'Confident', 'Active': 'Still ill'}).rename(columns={'Deaths': 'Departed'}).describe() 

# drop_duplicates & sort_by ... ascending & create_dataframe & count
## no_of_something = create dataframe from data with header 'Confirmed', 'Country/Region', 'Active' | drop duplicates | sort by 'Active' ascending | count 
no_of_something = pd.DataFrame(data, columns=['Confirmed', 'Country/Region', 'Active']).drop_duplicates().sort_values(['Active'], axis='index', ascending=[True]).shape[0] 

# group_by & intersection & drop_columns & count
## on data | group by 'Country/Region' | intersection other_df | drop columns 'Country/Region' | count 
data.groupby(['Country/Region']).merge(other_df).drop(columns=['Country/Region']).shape[0] 

# drop_duplicates & append_column & difference & save_to json
## on data | drop duplicates | append column 0 as 'New useless column' | save to 'training_examples/pandas/save_target.csv' as json 
data.drop_duplicates().assign(**{'New useless column': data.drop_duplicates().apply(lambda row: 0, axis=1).values}).to_json('training_examples/pandas/save_target.csv') 
