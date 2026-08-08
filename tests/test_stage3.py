from backend.agents import ExplanationAgent, RiskAgent, SelfCheckAgent
from backend.data import make_demo_transactions
from backend.model import train_model


def test_low_risk_skips_the_llm():
    model = train_model(make_demo_transactions(240))
    transaction = make_demo_transactions(1).iloc[0].copy()
    transaction["graph_collusion_score"] = 0.0
    risk = RiskAgent(model).analyse(transaction)
    risk["risk_tier"] = "low"
    assert ExplanationAgent().explain(transaction, risk)["llm_used"] is False


def test_unsafe_high_risk_routes_to_human_review():
    decision = SelfCheckAgent().review({"risk_tier": "high"}, {"hard_action_allowed": False, "validation_precision": .20})
    assert decision["final_action"] == "human review queue"
