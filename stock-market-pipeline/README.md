# 📈 Stock Market ETL Pipeline (Airflow & PostgreSQL)

A robust, containerized micro-batch ETL (Extract, Transform, Load) data pipeline that fetches near real-time stock market data, processes it, and stores it in a PostgreSQL database for downstream analytics. The entire workflow is orchestrated using Apache Airflow.



## 🛠 Tech Stack
* **Orchestration:** Apache Airflow
* **Processing:** Python, Pandas
* **Data Source:** `yfinance` API
* **Storage:** PostgreSQL
* **Infrastructure:** Docker & Docker Compose

## 🏗 Architecture & Data Flow
1. **Extract:** A Python script fetches minute-by-minute stock price and volume data using the `yfinance` library.
2. **Transform:** Data is cleaned, typed, and deduplicated.
3. **Load:** The raw data is loaded into a PostgreSQL `stock_prices` table using idempotency (Upserts / `ON CONFLICT DO NOTHING`) to prevent duplicates.
4. **Analyze:** Airflow's `PostgresOperator` triggers an SQL query to calculate rolling metrics (like moving averages and max prices) and stores them in a `stock_analytics` table.
5. **Orchestrate:** Airflow schedules and monitors this entire sequence every 5 minutes.

## 📂 Project Structure
```text
├── dags/
│   └── stock_market_dag.py     # The Airflow DAG definition
├── scripts/
│   └── fetch_data.py           # Python extraction and load script
├── docker-compose.yml          # Infrastructure setup (Airflow + Postgres)
├── .env                        # Environment variables (UID)
├── .gitignore                  # Git ignore rules
└── README.md