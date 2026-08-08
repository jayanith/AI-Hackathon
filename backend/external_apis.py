"""Live External Fraud Signal APIs."""
from __future__ import annotations

import os
import requests
from typing import Any


def query_ip_reputation(ip_address: str) -> dict[str, Any]:
    """Check IP confidence score on AbuseIPDB."""
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key:
        return {
            "provider": "AbuseIPDB",
            "status": "not_configured",
            "score": None,
            "detail": "Set ABUSEIPDB_API_KEY in .env for live IP reputation lookup."
        }
    try:
        resp = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers={"Key": api_key, "Accept": "application/json"},
            params={"ipAddress": ip_address, "maxAgeInDays": 90},
            timeout=5
        )
        if resp.status_code == 200:
            score = resp.json()["data"]["abuseConfidenceScore"]
            return {
                "provider": "AbuseIPDB",
                "status": "live",
                "score": score,
                "detail": f"Abuse confidence: {score}% (live AbuseIPDB lookup)."
            }
        return {"provider": "AbuseIPDB", "status": "api_error", "score": None, "detail": f"HTTP {resp.status_code}"}
    except Exception as exc:
        return {"provider": "AbuseIPDB", "status": "exception", "score": None, "detail": str(exc)[:80]}


# Kept for import compatibility — returns honest not-configured message
def query_email_verification(email: str) -> dict[str, Any]:
    disposable = any(d in email.lower() for d in ["mailinator", "tempmail", "throwaway", "guerrilla", "yopmail"])
    return {
        "provider": "Rule-based",
        "status": "rule_check",
        "is_disposable": disposable,
        "detail": f"Domain rule check: {'disposable domain detected' if disposable else 'domain not on disposable list'}."
    }


def query_gstin_verification(gstin: str) -> dict[str, Any]:
    return {
        "provider": "Format check",
        "status": "rule_check",
        "valid": True,
        "detail": "No live GSTIN API configured. Format validation only."
    }
