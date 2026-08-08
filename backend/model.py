"""Small, readable tabular fraud model. No deep learning or hidden service calls."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = ["TransactionAmt", "seller_tenure_days"]
CATEGORICAL_FEATURES = ["seller_id", "device_id", "email_domain", "card_type"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


@dataclass
class ModelBundle:
    pipeline: Pipeline
    metrics: dict[str, float | bool]


def train_model(transactions: pd.DataFrame) -> ModelBundle:
    """Train one interpretable logistic-regression classifier on the agreed columns."""
    train, validation = train_test_split(
        transactions, test_size=.25, random_state=42, stratify=transactions["isFraud"]
    )
    preprocessor = ColumnTransformer([
        ("numeric", Pipeline([("fill_missing", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUMERIC_FEATURES),
        ("categories", Pipeline([("fill_missing", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL_FEATURES),
    ])
    pipeline = Pipeline([
        ("prepare", preprocessor),
        ("classifier", LogisticRegression(max_iter=500, class_weight="balanced", random_state=42)),
    ])
    pipeline.fit(train[FEATURES], train["isFraud"])
    probabilities = pipeline.predict_proba(validation[FEATURES])[:, 1]
    precision, _, thresholds = precision_recall_curve(validation["isFraud"], probabilities)
    valid_thresholds = thresholds[precision[:-1] >= .95]
    hard_action_threshold = float(valid_thresholds[0]) if len(valid_thresholds) else 1.01
    operating_threshold = hard_action_threshold if hard_action_threshold <= 1 else .80
    predictions = (probabilities >= operating_threshold).astype(int)
    metrics = {
        "validation_auc": round(float(roc_auc_score(validation["isFraud"], probabilities)), 3),
        "validation_precision": round(float(precision_score(validation["isFraud"], predictions, zero_division=0)), 3),
        "validation_recall": round(float(recall_score(validation["isFraud"], predictions, zero_division=0)), 3),
        "hard_action_threshold": round(hard_action_threshold, 3),
        "hard_action_allowed": hard_action_threshold <= 1,
    }
    return ModelBundle(pipeline=pipeline, metrics=metrics)


def score_transactions(bundle: ModelBundle, transactions: pd.DataFrame) -> pd.DataFrame:
    """Add a base risk score only. Graph and actions arrive in later stages."""
    scored = transactions.copy()
    scored["base_risk_score"] = bundle.pipeline.predict_proba(scored[FEATURES])[:, 1].round(4)
    return scored
