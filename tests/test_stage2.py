import pandas as pd

from backend.graph import graph_scores


def test_shared_identifier_increases_collusion_score():
    transactions = pd.DataFrame({
        "TransactionID": [1, 2, 3], "TransactionAmt": [10, 20, 30],
        "seller_id": ["seller_a", "seller_b", "seller_c"],
        "device_id": ["shared_device", "shared_device", "private_device"],
        "email_domain": ["a.com", "b.com", "c.com"], "card_type": ["credit"] * 3,
        "seller_tenure_days": [10, 10, 100], "isFraud": [0, 1, 0],
        "address_id": ["shared_address", "shared_address", "private_address"],
    })
    scored, summary = graph_scores(transactions)
    assert summary["edges"] > 0
    assert scored.loc[0, "graph_collusion_score"] > scored.loc[2, "graph_collusion_score"]
