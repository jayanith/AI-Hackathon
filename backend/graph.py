"""Lightweight collusion scoring with NetworkX.

This is deliberately not a GNN. It makes a small actor graph from shared
identifiers and turns simple graph features into an explainable score.
"""
from __future__ import annotations

import networkx as nx
import pandas as pd

IDENTIFIER_COLUMNS = ("device_id", "ip_address", "address_id")


def _usable(value: object) -> bool:
    """Do not connect every actor through a missing/unknown identifier."""
    text = str(value).strip().lower()
    return bool(text) and text not in {"unknown", "nan", "none", "ieee_device_unknown"}


def build_actor_graph(transactions: pd.DataFrame) -> nx.Graph:
    """Create seller -> shared identifier edges, deduplicated for speed."""
    graph = nx.Graph()
    identifier_columns = [column for column in IDENTIFIER_COLUMNS if column in transactions.columns]
    for column in identifier_columns:
        pairs = transactions[["seller_id", column]].dropna().drop_duplicates()
        for seller, identifier in pairs.itertuples(index=False):
            if _usable(identifier):
                graph.add_edge(f"seller:{seller}", f"{column}:{identifier}", relation=column)
    return graph


def graph_scores(transactions: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Score sellers from degree and shared-neighbour counts.

    A seller has elevated risk when it is connected to identifiers used by
    multiple seller segments. This is evidence to review, not proof of fraud.
    """
    graph = build_actor_graph(transactions)
    seller_scores: dict[str, float] = {}
    seller_evidence: dict[str, str] = {}
    for seller in transactions["seller_id"].astype(str).unique():
        seller_node = f"seller:{seller}"
        if seller_node not in graph:
            seller_scores[seller] = 0.0
            seller_evidence[seller] = "No usable shared device/IP/address identifier"
            continue
        identifiers = list(graph.neighbors(seller_node))
        degree = len(identifiers)
        shared_neighbours = sum(max(graph.degree(identifier) - 1, 0) for identifier in identifiers)
        # Simple, bounded and visible: 40% local degree, 60% shared connections.
        score = min(1.0, .4 * min(degree / 5, 1) + .6 * min(shared_neighbours / 10, 1))
        seller_scores[seller] = round(score, 4)
        seller_evidence[seller] = f"{degree} linked identifiers; {shared_neighbours} links shared with other sellers"
    scored = transactions.copy()
    scored["graph_collusion_score"] = scored["seller_id"].astype(str).map(seller_scores).fillna(0.0)
    scored["graph_evidence"] = scored["seller_id"].astype(str).map(seller_evidence)
    summary = {"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges(), "seller_nodes": sum(1 for n in graph if n.startswith("seller:"))}
    return scored, summary
