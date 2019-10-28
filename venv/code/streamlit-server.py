import streamlit as st
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
import plotly
import plotly.express as px

st.title('Show model')

#establish sql connection and engine
engine = create_engine('mysql+mysqlconnector://USERNAME:PASSWORD@URL/DATABASENAME', echo=False)

@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

def load_db_data(engine):


    data = pd.read_sql('SELECT * FROM calculation_protocol', engine)

    return data

data_load_state = st.text('Loading data...')
data = load_db_data(engine)
data_load_state.text('Loading data... done!')

st.subheader('Model list')
if st.checkbox('Show dataframe'):
    st.write(data)

selection = st.multiselect('Show tables:', data['data_set_table'].unique())
#col1 = st.selectbox('Which feature on x?', data.columns[0:7])
#col2 = st.selectbox('Which feature on y?', data.columns[0:7])

new_df = data[(data['data_set_table'].isin(selection))]

# create figure using plotly express
fig = px.scatter(new_df, x ='run_id',y='error_mean', color='data_set_table')

# Plot!
st.plotly_chart(fig)
