"""Live SendGrid Notification API Integration.

Free tier: 100 emails/day forever.
Fires when an action (e.g. step-up verification, payout hold) is taken or an appeal is submitted.
"""
from __future__ import annotations

import os
import requests


def send_notification(recipient_email: str, subject: str, body_text: str) -> dict[str, str | bool]:
    """Send an email using SendGrid API v3.
    
    If SENDGRID_API_KEY is not set, returns an honest status dictionary without crashing.
    """
    api_key = os.getenv("SENDGRID_API_KEY")
    sender_email = os.getenv("SENDGRID_SENDER_EMAIL", "notifications@trustgraph.ai")

    if not api_key:
        return {
            "sent": False,
            "status": "not_configured",
            "message": "SENDGRID_API_KEY not set in environment. Email simulated locally."
        }

    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "personalizations": [
            {
                "to": [{"email": recipient_email}],
                "subject": subject,
            }
        ],
        "from": {"email": sender_email, "name": "TrustGraph AI Safety Engine"},
        "content": [
            {
                "type": "text/plain",
                "value": body_text,
            }
        ],
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=8)
        if response.status_code in (200, 201, 202):
            return {
                "sent": True,
                "status": "success",
                "message": f"Notification delivered to {recipient_email} via SendGrid API."
            }
        return {
            "sent": False,
            "status": "api_error",
            "message": f"SendGrid returned HTTP {response.status_code}: {response.text[:120]}"
        }
    except Exception as exc:
        return {
            "sent": False,
            "status": "exception",
            "message": f"Failed to reach SendGrid API: {str(exc)[:120]}"
        }
