import pandas as pd

from backend.data import REQUIRED_COLUMNS, ieee_to_stable_schema, make_demo_transactions
from backend.model import score_transactions, train_model


def test_stage1_model_scores_the_stable_input_schema():
    transactions = make_demo_transactions(240)
    assert set(REQUIRED_COLUMNS).issubset(transactions.columns)
    bundle = train_model(transactions)
    scored = score_transactions(bundle, transactions)
    assert scored["base_risk_score"].between(0, 1).all()
    assert "hard_action_allowed" in bundle.metrics


def test_ieee_adapter_keeps_the_same_model_schema():
    raw = pd.DataFrame({
        "TransactionID": [1, 2], "TransactionAmt": [99.0, 2500.0], "TransactionDT": [86400, 172800],
        "ProductCD": ["W", "C"], "card4": ["visa", "mastercard"], "addr1": [101, 202],
        "P_emaildomain": ["gmail.com", None], "DeviceInfo": ["SM-G950", None], "isFraud": [0, 1],
    })
    stable = ieee_to_stable_schema(raw)
    assert set(REQUIRED_COLUMNS).issubset(stable.columns)
    assert stable.loc[0, "seller_id"].startswith("ieee_segment_")
