
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


def connect(database: str | None = None) -> psycopg.Connection:
    """Connect to the database."""
    auth = f"{user}:{password}" if password else user
    dsn = f"postgresql://{auth}@{host}:{port}/{database or db}"
    return psycopg.connect(dsn)


def validateQuery(query: str) -> bool:
    """Validate a query is a valid SQL query. Which does not contain any SQL injection, delete, update, insert, drop, alter, grant, revoke, etc."""
    if "SELECT" in query:
        return True
    return False


def execute(query: str, conn: psycopg.Connection | None = None) -> None:
    """Execute a query and return the results."""
    if not validateQuery(query):
        raise ValueError("Invalid query")
    if conn is None:
        conn = connect()
        own_conn = True
    else:
        own_conn = False
    cur = conn.cursor(row_factory=dict_row)
    cur.execute(query)
    rows = cur.fetchall()
    conn.commit()
    cur.close()
    if own_conn:
        conn.close()
    return rows
    
# if __name__ == "__main__":
    # rows = execute("SELECT * FROM transactions where bank = 'CIBC' and debit_amount > 100")
    # rows = execute("delete from transactions")
    # print(rows)
