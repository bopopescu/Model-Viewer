# Data Loading Code Hidden Here
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import pymysql
import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from datetime import datetime

#defining sql needed data
db_url = 'mysql+mysqlconnector://USERNAME:PASSWORD@URL/DATABASENAME'

# ===== configuration ===== #
#file_path = 'train.csv'
file_path = '../data/cumulative.csv'

#naming
model_name = 'Kepler Model 01'
model_name_random_suffix = " random"
model_name_decision_suffix = " decision"
model_name_regression_suffix = " regression"

#model run config
model_runs = 10
feature_columns = ['koi_score',
                   'koi_fpflag_nt',
                   'koi_fpflag_ss',
                   'koi_fpflag_co',
                   'koi_fpflag_ec',
                   'koi_period',
                   'koi_period_err1',
                   'koi_period_err2',
                   'koi_time0bk',
                   'koi_time0bk_err1',
                   'koi_time0bk_err2',
                   'koi_impact',
                   'koi_impact_err1',
                   'koi_impact_err2',
                   'koi_duration',
                   'koi_duration_err1',
                   'koi_duration_err2',
                   'koi_depth',
                   'koi_depth_err1',
                   'koi_depth_err2',
                   'koi_prad',
                   'koi_prad_err1',
                   'koi_prad_err2',
                   'koi_teq',
                   'koi_insol',
                   'koi_insol_err1',
                   'koi_insol_err2',
                   'koi_model_snr',
                   'koi_tce_plnt_num',
                   'koi_steff',
                   'koi_steff_err1',
                   'koi_steff_err2',
                   'koi_slogg',
                   'koi_slogg_err1',
                   'koi_slogg_err2',
                   'koi_srad',
                   'koi_srad_err1',
                   'koi_srad_err2',
                   'ra',
                   'dec',
                   'koi_kepmag']

target_column = "koi_disposition"

push_i = 2

# ===== methods ===== #
#this function prepares the table which registers all future calculations to link the to tables with the data look at it like a list with all run models
def prepDB(engine):

    run_id = ['0']
    timestamp = ['00:00:00']
    label = ['label']
    #get date and time
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

    table_name = ['table_name']
    data_set_name = ['data_set_name']
    df = pd.DataFrame(data = {'run_id' : run_id,
                              'timestamp': date_time,
                              'label': label,
                              'table_name': table_name,
                              'data_set_table': data_set_name,
                              'error_mean': 0,
                              'run_count': 0})
    df.to_sql(name='calculation_protocol', con=engine, if_exists='replace', index=False)

    return 0

#pushes a data fram to the sql db
def push_data_set_to_db(engine, error_mean, run_time, table_name, data_set_name, run_id):

    # ====== Reading table ====== #
    # Reading Mysql table into a pandas DataFrame
    data = pd.read_sql('SELECT * FROM calculation_protocol', engine)

    #get time and date for registration
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

    #create append datafram for new row in table
    append = pd.DataFrame(data={'run_id': run_id,
                         'timestamp': date_time,
                         'label': table_name,
                         'table_name': table_name,
                         'data_set_table': data_set_name,
                         'error_mean': error_mean,
                         'run_time': run_time},index=[0])

    new_data = data.append(append, ignore_index=False, verify_integrity=False, sort=None)
    new_data.to_sql(name='calculation_protocol', con=engine, if_exists='replace', index=False)

    return 0

#creates new table with model results
def get_mae(max_nodes, train_X, val_X, train_y, val_y,rand):

    if rand == True :
        model = RandomForestRegressor(random_state=1)
    else:
        model = DecisionTreeRegressor(max_leaf_nodes=max_nodes, random_state=0)

    model.fit(train_X, train_y)
    preds_val = model.predict(val_X)
    mae = mean_absolute_error(val_y, preds_val)
    return(mae)



def get_mae_to_db(max_nodes, train_X, val_X, train_y, val_y):
    model = DecisionTreeRegressor(max_leaf_nodes=max_nodes, random_state=0)
    model.fit(train_X, train_y)
    preds_val = model.predict(val_X)
    mae = mean_absolute_error(val_y, preds_val)
    return(mae)

# ====== sql connection ====== #
# Connecting to mysql by providing a sqlachemy engine
engine = create_engine(db_url, echo=False)

# uncomment line bellow to prep db
prepDB(engine)

# Load data
test_data = pd.read_csv(file_path)

# SQL create table
test_data.to_sql(name=model_name, con=engine, if_exists='replace', index=False)

y = test_data.koi_disposition
X = test_data[feature_columns]
X = X.fillna(0)
X.to_sql(name=model_name, con=engine, if_exists='replace', index=False)

# split data
train_X, val_X, train_y, val_y = train_test_split(X, y, random_state = 0)

data = pd.read_sql('SELECT * FROM calculation_protocol', engine)

# compare MAE with differing values of max_leaf_nodes
for leaf_i in range(model_runs):
    # get time
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    mae_loop = get_mae(leaf_i+2, train_X, val_X, train_y, val_y,False)
    # create append dataframe for new row in table
    append = pd.DataFrame(data={'run_id': leaf_i+2,
                                'timestamp': date_time,
                                'label': model_name,
                                'table_name': model_name,
                                'data_set_table': model_name,
                                'error_mean': mae_loop,
                                'run_time': leaf_i+2}, index=[0])

    data = data.append(append, ignore_index=False, verify_integrity=False, sort=None)

# push the filled DF to the DB
data.to_sql(name='calculation_protocol', con=engine, if_exists='replace', index=False)



