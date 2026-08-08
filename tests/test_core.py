from trustgraph.core import build_demo_graph, decide_action, demo_transactions, score_row, train_risk_model

def test_demo_pipeline_and_policy_guardrail():
    data = demo_transactions(160)
    model, metrics, _ = train_risk_model(data)
    risk, evidence = score_row(data.iloc[0], model)
    assert 0 <= risk <= 1
    assert evidence
    action = decide_action(.99, .99, {"hard_action_enabled": False, "operating_precision": .5})
    assert action["action"] == "Payout hold"

def test_graph_has_collusion_nodes():
    graph, nodes = build_demo_graph()
    assert graph.has_edge("seller:S-204", "buyer:B-110")
    assert nodes.loc[nodes.node.eq("seller:S-204"), "graph_risk"].iloc[0] > 0
