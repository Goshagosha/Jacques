# Target
## target code = pandas
import pandas as pd

# load_from
## data = load from 'covid_19_data.csv' as csv_with_header 
data = pd.read_csv('covid_19_data.csv') 

# drop_columns & select_rows & group_by & union & join & sort_by ... descending & describe & show
## on data | drop columns 'Active', 'Country/Region' | select rows 'Confirmed' < 20 | group by 'Deaths' | union other_dataframe | join outer another_df on 'SNo' | sort by 'Recovered' descending | describe | show 
print(pd.concat([data.drop(columns=['Active', 'Country/Region'])['Confirmed' < 20].groupby(['Deaths']), other_dataframe]).join(another_df, on=['SNo'], how='outer').sort_values(['Recovered'], axis='index', ascending=[False]).describe()) 

# drop_duplicates & difference & apply max & sort_by ... ascending & head & apply mean & show_schema & save_to csv
## on data | drop duplicates | difference other_df | apply max on 'Deaths' as 'Most deaths' | sort by 'Active' ascending | head 250 | apply mean on 'Active' as 'Average active' | show schema | save to 'training_examples/pandas/save_target.csv' as csv 
data.drop_duplicates()[~data.drop_duplicates().isin(other_df).all(1)].agg({'Deaths' : 'max'}).rename(columns={'Deaths' : 'Most deaths'}).sort_values(['Active'], axis='index', ascending=[True]).head(250).agg({'Active' : 'mean'}).rename(columns={'Active' : 'Average active'}).info(verbose=False).to_csv('training_examples/pandas/save_target.csv') 

# group_by & intersection & apply sum & replace_values & apply max & apply min & describe & save_to csv
## on data | group by 'Active' | intersection some_other_df | apply sum on 'Active' as 'Total active' | replace 0 with 'Unknown' | apply max on 'Confirmed' as 'Most confirmed' | apply min on 'Confirmed' as 'Least confirmed' | describe | save to 'training_examples/pandas/save_target.csv' as csv 
data.groupby(['Active']).merge(some_other_df).agg({'Active' : 'sum'}).rename(columns={'Active' : 'Total active'}).replace(0, 'Unknown').agg({'Confirmed' : 'max'}).rename(columns={'Confirmed' : 'Most confirmed'}).agg({'Confirmed' : 'min'}).rename(columns={'Confirmed' : 'Least confirmed'}).describe().to_csv('training_examples/pandas/save_target.csv') 

# drop_columns & intersection & sort_by ... descending & rename_columns & sort_by ... ascending & drop_duplicates & count & show
## on data | drop columns 'Active' | intersection other_other_df | sort by 'Active' descending | rename columns 'Active' to 'Still ill' | sort by 'Still ill' ascending | drop duplicates | count | show 
print(data.drop(columns=['Active']).merge(other_other_df).sort_values(['Active'], axis='index', ascending=[False]).rename(columns={'Active': 'Still ill'}).sort_values(['Still ill'], axis='index', ascending=[True]).drop_duplicates().shape[0]) 

# create_dataframe & rename_columns & select_columns & append_column & append_column & apply sum & apply mean & select_columns
## this_new_dataframe = create dataframe from data with header 'Confirmed', 'Active', 'Deaths', 'Country/Region' | rename columns 'Active' to 'Still sick' | select columns 'Still sick', 'Active' | append column 0 as 'Zeroes' | append column 'Zeroes' + 1 as 'Ones' | apply sum on 'Zeroes' as 'More zeroes' | apply mean on 'Ones' as 'More ones' | select columns 'Zeroes', 'Ones' 
this_new_dataframe = pd.DataFrame(data, columns=['Confirmed', 'Active', 'Deaths', 'Country/Region']).rename(columns={'Active': 'Still sick'})[['Still sick', 'Active']].assign(**{'Zeroes': pd.DataFrame(data, columns=['Confirmed', 'Active', 'Deaths', 'Country/Region']).rename(columns={'Active': 'Still sick'})[['Still sick', 'Active']].apply(lambda row: 0, axis=1).values}).assign(**{'Ones': pd.DataFrame(data, columns=['Confirmed', 'Active', 'Deaths', 'Country/Region']).rename(columns={'Active': 'Still sick'})[['Still sick', 'Active']].assign(**{'Zeroes': pd.DataFrame(data, columns=['Confirmed', 'Active', 'Deaths', 'Country/Region']).rename(columns={'Active': 'Still sick'})[['Still sick', 'Active']].apply(lambda row: 0, axis=1).values}).apply(lambda row: 'Zeroes' + 1, axis=1).values}).agg({'Zeroes' : 'sum'}).rename(columns={'Zeroes' : 'More zeroes'}).agg({'Ones' : 'mean'}).rename(columns={'Ones' : 'More ones'})[['Zeroes', 'Ones']] 

# replace_values & difference & select_rows & union & count & save_to json
## on data | replace 12 with 'twelve' | difference 'some other table' | select rows 'Active' > 12 | union one_more_df | count | save to 'training_examples/pandas/save_target.csv' as json 
pd.concat([data.replace(12, 'twelve')[~data.replace(12, 'twelve').isin('some other table').all(1)]['Active' > 12], one_more_df]).shape[0].to_json('training_examples/pandas/save_target.csv') 

# create_dataframe & head & join & apply min & show_schema
## df1984 = create dataframe from data with header 'Active', 'Country/Region' | head 1000 | join right data on 'Country/Region' | apply min on 'Active' as 'Least active' | show schema 
df1984 = pd.DataFrame(data, columns=['Active', 'Country/Region']).head(1000).join(data, on=['Country/Region'], how='right').agg({'Active' : 'min'}).rename(columns={'Active' : 'Least active'}).info(verbose=False) 
