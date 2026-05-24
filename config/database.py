"""
Database configuration and query execution.
All SQL queries in the application go through the `query` function below.
"""

import psycopg2
import pandas as pd
import streamlit as st

DB_HOST = "localhost"
DB_NAME = "dvdrental"
DB_USER = "postgres"
DB_PASS = "123"


@st.cache_data(ttl=300, show_spinner=False)
def query(sql: str) -> pd.DataFrame:
    """Execute a SQL query and return the result as a DataFrame."""
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    df   = pd.read_sql(sql, conn)
    conn.close()
    return df
