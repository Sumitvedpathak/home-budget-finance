"""PostgreSQL database setup for budget-finance."""

import os

import psycopg
from psycopg.rows import dict_row

# Connection parameters from environment variables
db = os.environ.get("PGDATABASE", "budget_finance")
user = os.environ.get("PGUSER", "postgres")
password = os.environ.get("PGPASSWORD", "sa")
host = os.environ.get("PGHOST", "localhost")
port = os.environ.get("PGPORT", "5432")

TABLE_NAME = "transactions"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id SERIAL PRIMARY KEY,
    bank VARCHAR(100),
    account_type VARCHAR(100),
    # account_number VARCHAR(100),
    name VARCHAR(255),
    date DATE,
    category VARCHAR(255),
    description TEXT,
    debit_amount DECIMAL(15, 2),
    credit_amount DECIMAL(15, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

INSERT_SQL = f"""
INSERT INTO {TABLE_NAME}
(bank, account_type, name, date, category, description, debit_amount, credit_amount)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""



def connect(database: str | None = None) -> psycopg.Connection:
    """Connect to the database."""
    auth = f"{user}:{password}" if password else user
    dsn = f"postgresql://{auth}@{host}:{port}/{database or db}"
    return psycopg.connect(dsn)


def createDb(database: str | None = None) -> None:
    """Check if database exists; create it if not."""
    target = database or db
    conn = connect("postgres")  # must use existing db to create another
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target,))
    if cur.fetchone() is None:
        cur.execute(f'CREATE DATABASE "{target}"')
    cur.close()
    conn.close()


def createTable(conn: psycopg.Connection | None = None) -> None:
    """Check if table exists; create it if not."""
    if conn is None:
        conn = connect()
        own_conn = True
    else:
        own_conn = False
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(CREATE_TABLE_SQL)
    cur.close()
    if own_conn:
        conn.close()


def insertTransaction(
    bank: str | None = None,
    account_type: str | None = None,
    # account_number: str | None = None,
    name: str | None = None,
    date: str | None = None,
    category: str | None = None,
    description: str | None = None,
    debit_amount: float | None = None,
    credit_amount: float | None = None,
    conn: psycopg.Connection | None = None,
) -> None:
    """Insert a single record into the transactions table."""
    if conn is None:
        conn = connect()
        own_conn = True
    else:
        own_conn = False
    cur = conn.cursor()
    cur.execute(
        INSERT_SQL,
        (
            bank,
            account_type,
            # account_number,
            name,
            date,
            category,
            description,
            debit_amount,
            credit_amount,
        ),
    )
    conn.commit()
    cur.close()
    if own_conn:
        conn.close()


def getAllTransactions(conn: psycopg.Connection | None = None) -> list[dict]:
    """Fetch all records from the transactions table."""
    if conn is None:
        conn = connect()
        own_conn = True
    else:
        own_conn = False
    cur = conn.cursor(row_factory=dict_row)
    cur.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cur.fetchall()
    cur.close()
    if own_conn:
        conn.close()
    return rows


if __name__ == "__main__":
    createDb()
    createTable()
    print(f"Database and table '{TABLE_NAME}' are ready.")
    transactions = getAllTransactions()
    print(transactions)
