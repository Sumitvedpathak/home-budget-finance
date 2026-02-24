from datetime import datetime

from load import insertTransaction


def transform_records(records: list[dict], filename: str) -> list[dict]:
    """Transform a list of records from extract into the canonical transaction schema.

    Args:
        records: List of row dicts from extract (e.g. DataFrame.to_dict('records')).
        filename: Source filename (e.g. 'cibc-dec.csv') - used to infer bank.

    Returns:
        List of dicts with keys: bank, account_type, account_number, name, date,
        category, description, debit_amount, credit_amount.
    """
    transformed = []
    for record in records:
        name = filename.lower().split(".")[0]
        if "cibc" in name:
            transformed.append(_transform_cibc_record(record))
        elif "scotia" in name:
            transformed.append(_transform_scotia_record(record))
        elif "rbc" in name:
            transformed.append(_transform_rbc_record(record))
        elif "nbc" in name:
            transformed.append(_transform_nbc_record(record))
        elif "walmart" in name:
            transformed.append(_transform_walmart_record(record))
        insertTransaction(bank=transformed[-1]["bank"], account_type=transformed[-1]["account_type"], account_number=transformed[-1]["account_number"], 
        name=transformed[-1]["name"], date=transformed[-1]["date"], category=transformed[-1]["category"], description=transformed[-1]["description"], 
        debit_amount=transformed[-1]["debit_amount"], credit_amount=transformed[-1]["credit_amount"])
    return transformed


def _transform_cibc_record(record: dict) -> dict:
    """Map a single raw record to the canonical schema."""
    return {
        "bank": "CIBC",
        "account_type": "Credit Card",
        "account_number": record.get("Account Number") or record.get("account_number") or None,
        "name": None,
        "date": _parse_date(record.get("Date") or record.get("date")),
        "category": None,
        "description": record.get("Description") or record.get("description") or None,
        "debit_amount": _parse_amount(record.get("Debit") or record.get("Debit Amount") or record.get("Amount")),
        "credit_amount": _parse_amount(record.get("Credit") or record.get("Credit Amount") or record.get("Amount")),
    }

def _transform_nbc_record(record: dict) -> dict:
    """Map a single raw record to the canonical schema."""
    return {
        "bank": "NBC",
        "account_type": "Chequing",
        "account_number": None,
        "name": None,
        "date": _parse_date(record.get("Date") or record.get("date")),
        "category": record.get("Category") or record.get("category") or None,
        "description": record.get("Description") or record.get("description") or None,
        "debit_amount": _parse_amount(record.get("Debit") or record.get("Debit Amount") or record.get("Amount")),
        "credit_amount": _parse_amount(record.get("Credit") or record.get("Credit Amount") or record.get("Amount")),
    }

def _transform_rbc_record(record: dict) -> dict:
    """Map a single raw record to the canonical schema."""
    credit_amount = 0
    debit_amount = 0
    if _parse_amount(record.get("AmountCAD")) > 0: 
        credit_amount = _parse_amount(record.get("AmountCAD"))
    else:
        debit_amount = _parse_amount(record.get("AmountCAD"))

    return {
       "bank": "RBC",
        "account_type": record.get("Account Type") or None,
        "account_number": record.get("Account Number") or None,
        "name": None,
        "date": _parse_date(record.get("Transaction Date")),
        "category": None,
        "description": " ".join(s for s in [_str_or_empty(record.get("Description 1")), _str_or_empty(record.get("Description 2"))] if s) or None,
        "debit_amount": debit_amount,
        "credit_amount": credit_amount,
    }

def _transform_scotia_record(record: dict) -> dict:
    """Map a single raw record to the canonical schema."""
    credit_amount = 0
    debit_amount = 0
    if _parse_amount(record.get("Amount")) > 0:
        credit_amount = _parse_amount(record.get("Amount"))
    else:
        debit_amount = _parse_amount(record.get("Amount"))
    return {
        "bank": "Scotia",
        "account_type": "Chequing",
        "account_number": None,
        "name": None,
        "date": _parse_date(record.get("Date") or record.get("date")),
        "category": None,
        "description": " ".join(s for s in [_str_or_empty(record.get("Description")), _str_or_empty(record.get("Sub-description"))] if s) or None,
        "debit_amount": debit_amount,
        "credit_amount": credit_amount,
    }

def _transform_walmart_record(record: dict) -> dict:
    """Map a single raw record to the canonical schema."""
    credit_amount = 0
    debit_amount = 0
    if _parse_amount(record.get("Amount")) > 0:
        debit_amount = _parse_amount(record.get("Amount"))
    else:
        credit_amount = _parse_amount(record.get("Amount"))
    return {
        "bank": "Walmart",
        "account_type": "Credit Card",
        "account_number": record.get("Transaction Card Number") or None,
        "name": record.get("Name on Card") or None,
        "date": _parse_date(record.get("Date") or record.get("date")),
        "category": record.get("Merchant Category") or None,
        "description": record.get("Merchant Name") or None,
        "debit_amount": debit_amount,
        "credit_amount": credit_amount,
    }

def _parse_date(val) -> str | None:
    """Convert date from mm/dd/yyyy to yyyy-mm-dd. Returns None for invalid/empty."""
    if val is None or (isinstance(val, float) and val != val) or val == "":
        return None
    s = str(val).strip()
    if not s or s.lower() == "nan":
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _str_or_empty(val) -> str:
    """Return empty string for None/NaN, else stripped string. For safe join."""
    if val is None or (isinstance(val, float) and val != val):
        return ""
    s = str(val).strip()
    return "" if s.lower() == "nan" else s


def _parse_amount(val) -> float | None:
    """Parse amount string to float, handling negatives and currency symbols."""
    if val is None or val == "" or (isinstance(val, float) and val != val):  # NaN check
        return None
    s = str(val).replace("$", "").replace(",", "").strip()
    if not s or s == "-":
        return None
    try:
        return float(s)
    except ValueError:
        return None
