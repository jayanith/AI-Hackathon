# TrustGraph AI

An explainable, multi-agent graph-aware fraud-control dashboard powered by Google Gemini AI (`@google/genai` SDK).

## Quick Start (Full-Stack Web App)

```bash
npm install
npm run dev
```

Open `http://localhost:3000` to launch the TrustGraph AI Control Panel.

## Environment Setup

Copy `.env.example` to `.env` and add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key
ABUSEIPDB_API_KEY=optional_abuseipdb_key
```

## System Architecture

```text
IEEE-CIS Dataset + Live Signals -> Risk Agent -> Policy Agent -> Action / Human Review
Actor Events -> NetworkX Graph Agent -> Network Risk -^
                                            |-> Gemini AI Explanation + Audit Log + Appeal Workflow
Fairness Agent -> Cohort Parity Monitoring -^
```

## Production Capabilities

- **3-Agent Multi-Agent Orchestration:** Tabular Risk Scoring, Gemini AI Explanation Generation, and Self-Check Compliance.
- **Graph Anomaly Engine:** Identifies shared device rings, IP subnets, and seller-buyer collusion networks.
- **Livelihood Guardrails & SLA:** Automatic 24h human review routing for high-impact payout holds with append-only audit trail and appeal handling.
- **Real-Time Signal Verification:** Integrated IP reputation (AbuseIPDB), domain verification, and GSTIN format checks.

