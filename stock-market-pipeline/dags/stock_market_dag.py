from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
import sys

# Add the scripts folder to the system path so Airflow can find your module
sys.path.insert(0, '/opt/airflow/scripts')
from fetch_data import fetch_and_store_stock_data

default_args = {
    'owner': 'data_engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'stock_market_microbatch',
    default_args=default_args,
    description='Fetch stock data and generate analytics every 5 mins',
    schedule_interval=timedelta(minutes=5),
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # Task 1: Fetch and load data
    fetch_data = PythonOperator(
        task_id='fetch_AAPL_data',
        python_callable=fetch_and_store_stock_data,
        op_kwargs={'ticker_symbol': 'AAPL'}
    )

    # Task 2: Generate Analytics using PostgresOperator
    generate_analytics = PostgresOperator(
        task_id='calculate_moving_average',
        postgres_conn_id='postgres_default', # We will configure this in the UI
        sql="""
            INSERT INTO stock_analytics (ticker, avg_price, max_price, calculation_time)
            SELECT 
                ticker,
                AVG(price) as avg_price,
                MAX(price) as max_price,
                NOW() as calculation_time
            FROM stock_prices
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
            GROUP BY ticker;
        """
    )

    # Set execution order
    fetch_data >> generate_analytics