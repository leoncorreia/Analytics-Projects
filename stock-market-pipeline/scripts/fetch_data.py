import yfinance as yf
import pandas as pd
import psycopg2
from datetime import datetime

def fetch_and_store_stock_data(ticker_symbol):
    # 1. Connect to PostgreSQL (using the credentials from docker-compose)
    conn = psycopg2.connect(
        dbname="airflow", 
        user="airflow", 
        password="airflow", 
        host="postgres" # This matches the service name in docker-compose.yml
    )
    cursor = conn.cursor()

    # 2. Ensure tables exist (Notice the new UNIQUE constraint)
    create_tables_query = """
    CREATE TABLE IF NOT EXISTS stock_prices (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR(10),
        price DECIMAL(10, 2),
        volume BIGINT,
        timestamp TIMESTAMP,
        UNIQUE(ticker, timestamp) 
    );
    CREATE TABLE IF NOT EXISTS stock_analytics (
        ticker VARCHAR(10),
        avg_price DECIMAL(10, 2),
        max_price DECIMAL(10, 2),
        calculation_time TIMESTAMP
    );
    """
    cursor.execute(create_tables_query)
    conn.commit()

    # 3. Extract Data via yfinance
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period="1d", interval="1m")
    
    if data.empty:
        print(f"No data fetched for {ticker_symbol}.")
        return

    # 4. Transform Data
    latest_data = data.tail(1)
    price = float(latest_data['Close'].iloc[0])
    volume = int(latest_data['Volume'].iloc[0])
    timestamp = latest_data.index[0].to_pydatetime()
    
    # 5. Load Data (ON CONFLICT)
    insert_query = """
        INSERT INTO stock_prices (ticker, price, volume, timestamp)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ticker, timestamp) DO NOTHING;
    """
    cursor.execute(insert_query, (ticker_symbol, price, volume, timestamp))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Successfully inserted {ticker_symbol} data at {timestamp}")