"""Transaction loading and feature preparation.

The pipeline accepts the same columns whether they come from demo data or a CSV.
When the team receives a real dataset, set TRANSACTION_DATA_PATH to that file.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = [
    "TransactionID", "TransactionAmt", "seller_id", "device_id", "email_domain",
    "card_type", "seller_tenure_days", "isFraud",
]


def make_demo_transactions(rows: int = 500, seed: int = 42) -> pd.DataFrame:
    """Temporary fallback so the backend runs before the team supplies its generator."""
    rng = np.random.default_rng(seed)
    frame = pd.DataFrame({
        "TransactionID": range(1, rows + 1),
        "TransactionAmt": np.round(rng.lognormal(mean=7.0, sigma=0.8, size=rows), 2),
        "seller_id": rng.choice([f"seller_{i:03}" for i in range(1, 41)], rows),
        "device_id": rng.choice([f"device_{i:03}" for i in range(1, 180)], rows),
        "email_domain": rng.choice(["gmail.com", "outlook.com", "yahoo.com", "mailinator.com"], rows),
        "card_type": rng.choice(["credit", "debit", "prepaid"], rows, p=[.6, .32, .08]),
        "seller_tenure_days": rng.integers(1, 1200, rows),
        "address_id": rng.choice([f"address_{i:03}" for i in range(1, 120)], rows),
    })
    # This makes a reproducible, learnable demo label. It is not a real-world fraud rule.
    suspicious = (
        (frame["TransactionAmt"] > frame["TransactionAmt"].quantile(.90))
        | frame["email_domain"].eq("mailinator.com")
        | ((frame["card_type"] == "prepaid") & (frame["seller_tenure_days"] < 60))
    )
    frame["isFraud"] = (suspicious & (rng.random(rows) > .25)).astype(int)
    return frame


def load_transactions(path: str | None = None) -> tuple[pd.DataFrame, str]:
    """Load a prepared CSV, raw IEEE-CIS data, or the demo fallback.

    Detection happens by column names, so the model always receives the same
    stable schema. Supplying a real IEEE path therefore does not change model code.
    """
    csv_path = Path(path or os.getenv("TRANSACTION_DATA_PATH", "data/transactions.csv"))
    if csv_path.exists():
        raw = pd.read_csv(csv_path)
        if {"ProductCD", "card4", "TransactionDT"}.issubset(raw.columns):
            frame = ieee_to_stable_schema(raw)
            source = f"IEEE-CIS CSV: {csv_path}"
        else:
            frame, source = raw, f"CSV: {csv_path}"
    elif (Path("data/ieee/train_transaction.csv")).exists():
        frame = load_ieee_sample()
        source = "IEEE-CIS Fraud Detection (real labelled sample)"
    else:
        frame, source = make_demo_transactions(), "demo fallback (replace with your generator CSV)"
    missing = set(REQUIRED_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Transaction data is missing required columns: {sorted(missing)}")
    # Relationship columns are optional: a generator can add IP/address later
    # without forcing a change to the tabular-model input contract.
    graph_columns = [column for column in ("ip_address", "address_id") if column in frame.columns]
    return frame[REQUIRED_COLUMNS + graph_columns].copy(), source


def load_ieee_sample(max_rows: int | None = None) -> pd.DataFrame:
    """Read only useful IEEE columns for a fast local MVP, then merge device details.

    The full competition file is large. 120,000 rows is enough for an honest
    hackathon validation run and keeps startup time reasonable on a laptop.
    Set IEEE_MAX_ROWS to increase it when you have time.
    """
    max_rows = max_rows or int(os.getenv("IEEE_MAX_ROWS", "120000"))
    transaction_path = Path("data/ieee/train_transaction.csv")
    identity_path = Path("data/ieee/train_identity.csv")
    tx_columns = ["TransactionID", "TransactionAmt", "TransactionDT", "ProductCD", "card4", "addr1", "P_emaildomain", "isFraud"]
    transactions = pd.read_csv(transaction_path, usecols=tx_columns, nrows=max_rows)
    if identity_path.exists():
        identity = pd.read_csv(identity_path, usecols=["TransactionID", "DeviceType", "DeviceInfo"])
        transactions = transactions.merge(identity, on="TransactionID", how="left")
    return ieee_to_stable_schema(transactions)


def ieee_to_stable_schema(ieee: pd.DataFrame) -> pd.DataFrame:
    """Map IEEE columns into the simple product schema with explicit proxy names.

    IEEE is an anonymised payment dataset, not a marketplace dataset. It has no
    actual seller or tenure fields; the derived values below are modelling
    proxies and must be described that way in the presentation.
    """
    frame = pd.DataFrame()
    frame["TransactionID"] = ieee["TransactionID"]
    frame["TransactionAmt"] = ieee["TransactionAmt"]
    # Product + merchant location segment is a seller-like grouping proxy.
    frame["seller_id"] = "ieee_segment_" + ieee["ProductCD"].fillna("unknown").astype(str) + "_" + ieee["addr1"].fillna(-1).astype(str)
    # Prefer device info; use a stable fallback so missing identities are still scoreable.
    device = ieee.get("DeviceInfo", pd.Series("unknown", index=ieee.index)).fillna("unknown").astype(str)
    frame["device_id"] = "ieee_device_" + device
    frame["email_domain"] = ieee["P_emaildomain"].fillna("unknown").astype(str)
    frame["card_type"] = ieee["card4"].fillna("unknown").astype(str)
    # TransactionDT is seconds since the competition reference point; days elapsed is a time proxy, not true seller tenure.
    frame["seller_tenure_days"] = (ieee["TransactionDT"].fillna(0) / 86_400).astype(int)
    frame["isFraud"] = ieee["isFraud"].astype(int)
    # addr1 is an anonymised location code, so it is only an address-like proxy.
    frame["address_id"] = "ieee_address_" + ieee["addr1"].fillna(-1).astype(str)
    return frame
