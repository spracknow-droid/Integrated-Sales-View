# data_processor.py
import pandas as pd
import sqlite3

def fetch_integrated_data(db_path):
    """DB에서 데이터를 읽어와 DataFrame으로 반환"""
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM view_integrated_sales", conn)
        return df
    finally:
        conn.close()
