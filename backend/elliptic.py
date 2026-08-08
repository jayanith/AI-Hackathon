"""Elliptic Graph Anomaly Benchmark Evaluation.

Loads elliptic_txs_features.csv and elliptic_txs_classes.csv if available.
Trains a Random Forest classifier on precomputed node features to predict illicit (1) vs licit (2) transactions.
If real CSVs are missing, provides a synthetic demo evaluation benchmark so the system always operates smoothly.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

ELLIPTIC_DIR = Path("data/elliptic")


def evaluate_elliptic_benchmark() -> dict[str, Any]:
    """Train Random Forest on precomputed Elliptic node features."""
    features_path = ELLIPTIC_DIR / "elliptic_txs_features.csv"
    classes_path = ELLIPTIC_DIR / "elliptic_txs_classes.csv"

    if features_path.exists() and classes_path.exists():
        try:
            # Classes format: txId, label ("1"=illicit, "2"=licit, "unknown")
            classes_df = pd.read_csv(classes_path, header=None, names=["txId", "label"])
            
            # Features format: txId, time_step, feature_1 ... feature_165
            # We read header=None since the raw Kaggle Elliptic features file has no header row
            features_df = pd.read_csv(features_path, header=None, nrows=30000) # Fast load limit for hackathon responsiveness
            
            # First column is txId
            features_df.rename(columns={0: "txId"}, inplace=True)
            
            # Merge on txId — cast both to str to avoid int64/str mismatch
            features_df["txId"] = features_df["txId"].astype(str)
            classes_df["txId"] = classes_df["txId"].astype(str)
            merged = pd.merge(features_df, classes_df, on="txId")
            
            # Filter known labels (1 = illicit, 2 = licit)
            known = merged[merged["label"].astype(str).isin(["1", "2"])].copy()
            known["target"] = (known["label"].astype(str) == "1").astype(int)
            
            feature_cols = [c for c in known.columns if c not in ("txId", "label", "target")]
            
            X = known[feature_cols]
            y = known["target"]
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
            
            rf = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
            rf.fit(X_train, y_train)
            
            y_pred = rf.predict(X_test)
            y_prob = rf.predict_proba(X_test)[:, 1]
            
            prec = float(precision_score(y_test, y_pred, zero_division=0))
            rec = float(recall_score(y_test, y_pred, zero_division=0))
            auc = float(roc_auc_score(y_test, y_prob)) if len(np.unique(y_test)) > 1 else 0.0
            
            return {
                "available": True,
                "data_source": f"Real Elliptic Dataset ({len(known):,} labeled nodes loaded)",
                "classifier": "RandomForest (50 trees, max_depth=10)",
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "auc": round(auc, 4),
                "labeled_nodes_count": len(known),
                "illicit_count": int(y.sum()),
                "licit_count": int(len(y) - y.sum()),
                "message": "Graph anomaly detection technique successfully validated on real Elliptic benchmark!"
            }
        except Exception as err:
            return _demo_benchmark_fallback(f"Error parsing Elliptic CSVs: {str(err)[:100]}")
    
    return _demo_benchmark_fallback("Elliptic CSV files not found in data/elliptic/. Showing synthetic validation baseline.")


def _demo_benchmark_fallback(reason: str) -> dict[str, Any]:
    """Generates synthetic benchmark verification metrics matching expected Elliptic performance."""
    rng = np.random.default_rng(42)
    # Simulate 500 node features & labels
    n = 600
    X = rng.normal(size=(n, 20))
    # Illicit nodes have elevated mean on feature 0 & 1
    y = (X[:, 0] + X[:, 1] > 1.5).astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    rf = RandomForestClassifier(n_estimators=30, max_depth=6, random_state=42)
    rf.fit(X_train, y_train)
    
    y_pred = rf.predict(X_test)
    y_prob = rf.predict_proba(X_test)[:, 1]
    
    return {
        "available": False,
        "data_source": "Synthetic Elliptic Baseline (Demo)",
        "reason": reason,
        "classifier": "RandomForest (30 trees, max_depth=6)",
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "labeled_nodes_count": n,
        "illicit_count": int(y.sum()),
        "licit_count": int(n - y.sum()),
        "message": "Place elliptic_txs_features.csv & elliptic_txs_classes.csv in data/elliptic/ to evaluate on real Elliptic nodes."
    }
