import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# I define the database name. SQLite creates a single file.
DB_NAME = "hardware_store.db"

def get_engine():
    """
    I create a connection engine for pandas to write to SQL.
    """
    return create_engine(f'sqlite:///{DB_NAME}')

def save_to_sql(df, table_name):
    """
    I save a dataframe to the SQLite database.
    I use 'replace' to overwrite old simulation data with new scenarios.
    """
    engine = get_engine()
    try:
        # index=False means I don't want the pandas row numbers in my SQL table
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        print(f"   -> Table '{table_name}' saved to SQL successfully.")
    except Exception as e:
        print(f"   -> Error saving {table_name}: {e}")

def load_from_sql(table_name):
    """
    I read data back from SQL to show it in the app if needed.
    """
    engine = get_engine()
    return pd.read_sql(table_name, con=engine)