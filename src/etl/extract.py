"""Read CSV files from the statements folder."""

from pathlib import Path

import pandas as pd
from etl.trasform import transform_records

transactions = []

def read_statements(csv_path: Path) -> dict[Path, pd.DataFrame]:
    """Read all CSV files from the statements folder, including subfolders.

    Returns a dict mapping each file path to its DataFrame.
    """
    df = pd.read_csv(csv_path)
    filename = csv_path.name
    transformed = transform_records(df.to_dict("records"), filename)
    return transformed

def extract_statements(statements_dir: Path | str | None = None) -> dict[Path, pd.DataFrame]:
    """Extract all statements from the statements folder, including subfolders.
    """
    base = Path(__file__).resolve().parent.parent
    statements_dir = Path(statements_dir) if statements_dir else base / "statements/dec"
    for csv_path in statements_dir.rglob("*.csv"):
        transformed = read_statements(csv_path)
        transactions.append(transformed)
    print(transactions)
    return transactions

if __name__ == "__main__":
    transactions = extract_statements()
