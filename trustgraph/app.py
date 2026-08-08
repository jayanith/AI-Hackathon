from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[1]))
from trustgraph.core import (api_signals, append_audit, build_demo_graph, decide_action, elliptic_benchmark,
    fairness_report, load_ieee, read_audits, score_row, submit_appeal, train_risk_model)

load_dotenv()
st.set_page_config(page_title="TrustGraph AI", page_icon="🛡️", layout="wide")
st.markdown("""<style>.stApp{background:#f6f8f7}.risk-card{padding:1rem;border-radius:.7rem;background:#fff;border:1px solid #e2e8e4}.guardrail{padding:.8rem;border-left:4px solid #16815e;background:#e9f7ef;border-radius:.3rem}</style>""", unsafe_allow_html=True)

@st.cache_resource
def data_and_model():
    df, message = load_ieee()
    model, metrics, scored = train_risk_model(df)
    return df, message, model, metrics, scored

df, source_message, model, metrics, scored = data_and_model()
graph, graph_nodes = build_demo_graph()

st.sidebar.title("🛡️ TrustGraph AI")
st.sidebar.caption("India Region • Mumbai | DPDP-ready design")
page = st.sidebar.radio("Navigate", ["Command Center", "Investigation Case", "Collusion Graph", "Appeals & SLA", "Fairness & Governance"])
st.sidebar.divider()
st.sidebar.metric("Validation precision", f"{metrics['operating_precision']:.1%}")
st.sidebar.caption("Hard actions require ≥95% precision")

if page == "Command Center":
    st.title("Trust & Safety Command Center")
    st.info(source_message)
    a,b,c,d = st.columns(4)
    a.metric("Transactions analysed", f"{len(df):,}")
    b.metric("Fraud-model AUC", f"{metrics['auc']:.3f}")
    c.metric("High-risk graph ring", "1 active")
    d.metric("Hard action safety", "Enabled" if metrics["hard_action_enabled"] else "Human review only")
    st.markdown("### Prioritised investigator queue")
    queue = pd.DataFrame([
        ["CASE-204", "S-204 / seller collusion ring", "92%", "Payout hold", "Graph + identity"],
        ["CASE-188", "B-483 / transaction anomaly", "68%", "Step-up verification", "Tabular model"],
        ["CASE-177", "D-88 / delivery partner overlap", "74%", "Payout hold", "Graph + IP"],
    ], columns=["Case", "Actor / pattern", "Combined risk", "Recommended action", "Evidence"])
    st.dataframe(queue, use_container_width=True, hide_index=True)
    st.markdown("### Agent self-check")
    st.markdown("<div class='guardrail'>✓ Evidence is human-readable &nbsp; ✓ Income-impacting action has appeal route &nbsp; ✓ Hard-action precision guardrail evaluated &nbsp; ✓ Cohort fairness tracked</div>", unsafe_allow_html=True)

elif page == "Investigation Case":
    st.title("Investigation: CASE-204")
    row = df.iloc[min(3, len(df)-1)].copy()
    row["TransactionAmt"] = max(float(row.get("TransactionAmt", 0)), 4200)
    row["C1"] = max(float(row.get("C1", 0)), 8)
    row["P_emaildomain"] = "mailinator.com"
    risk, evidence = score_row(row, model)
    graph_risk = float(graph_nodes.loc[graph_nodes.node.eq("seller:S-204"), "graph_risk"].iloc[0])
    decision = decide_action(risk, graph_risk, metrics)
    x,y,z = st.columns(3)
    x.metric("Transaction model risk", f"{risk:.0%}")
    y.metric("Network anomaly risk", f"{graph_risk:.0%}")
    z.metric("Combined risk", decision["combined_risk"])
    st.subheader(decision["action"])
    st.caption(decision["route"])
    left,right = st.columns(2)
    with left:
        st.markdown("#### Explainable evidence")
        for item in evidence: st.write("• " + item)
        st.write("• Seller is connected to 3 buyers through shared device, IP and address")
        st.write("• Delivery partner D-88 shares suspicious IP with a buyer")
    with right:
        st.markdown("#### Live risk-signal adapters")
        st.dataframe(pd.DataFrame(api_signals("45.12.8.9", "demo@mailinator.com")), use_container_width=True, hide_index=True)
    if st.button("Record policy decision in immutable audit trail", type="primary"):
        append_audit({"event":"policy_decision", "case_id":"CASE-204", "risk":risk, "graph_risk":graph_risk, "decision":decision, "evidence":evidence})
        st.success("Audit event appended. This decision is reviewable and appealable.")

elif page == "Collusion Graph":
    st.title("Collusion Graph: network-level fraud evidence")
    pos = nx.spring_layout(graph, seed=8)
    edge_x, edge_y = [], []
    for u,v in graph.edges(): edge_x += [pos[u][0],pos[v][0],None]; edge_y += [pos[u][1],pos[v][1],None]
    fig = go.Figure(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(color="#9ab8aa", width=1), hoverinfo="none"))
    colors = {"seller":"#d9485f", "buyer":"#2f80ed", "delivery":"#e59b28", "device":"#8559a6", "ip":"#8559a6", "address":"#8559a6"}
    for kind in graph_nodes.type.unique():
        nodes = [n for n in graph.nodes if n.split(":")[0] == kind]
        fig.add_trace(go.Scatter(x=[pos[n][0] for n in nodes], y=[pos[n][1] for n in nodes], mode="markers+text", text=[n.split(":")[1] for n in nodes], textposition="top center", name=kind.title(), marker=dict(size=18, color=colors.get(kind,"#607d6f"))))
    fig.update_layout(height=560, showlegend=True, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig, use_container_width=True)
    st.warning("Why this matters: a transaction-only model cannot see that three buyers, the seller and delivery partner share hidden identifiers. Graph Agent escalates this collusion ring.")
    benchmark = elliptic_benchmark()
    st.subheader("Elliptic graph benchmark")
    st.json(benchmark)

elif page == "Appeals & SLA":
    st.title("Appeals: livelihood guardrail")
    st.write("Every income-impacting action is time-bound, explainable, and routed to a human reviewer.")
    with st.form("appeal"):
        case = st.selectbox("Case", ["CASE-204", "CASE-177"])
        actor = st.text_input("Actor", "S-204")
        statement = st.text_area("Appeal statement", "The orders are legitimate. Please review the evidence.")
        submitted = st.form_submit_button("Submit appeal")
    if submitted:
        event = submit_appeal(case, actor, statement)
        st.success(f"Appeal submitted. Human-review SLA: {event['sla_due']}")
    audits = read_audits()
    st.subheader("Immutable audit trail")
    st.dataframe(pd.DataFrame(audits[-20:]) if audits else pd.DataFrame([{ "status":"No decisions recorded yet"}]), use_container_width=True, hide_index=True)

else:
    st.title("Fairness & Governance")
    report = fairness_report()
    st.dataframe(report, use_container_width=True, hide_index=True)
    st.plotly_chart(px.bar(report, x="cohort", y="action_rate", color="cohort", title="Action-rate parity by protected operational cohort"), use_container_width=True)
    st.markdown("""#### Governance controls
    - **Data residency:** production PII must stay in India-region infrastructure.
    - **Safety threshold:** suspension/payout freeze requires ≥95% validation precision; otherwise human review.
    - **Auditability:** model evidence, policy decision, reviewer decision and appeal are append-only audit events.
    - **Cost:** classical model inference is near-zero; cached IP/email enrichments are invoked only for escalated cases.
    """)
