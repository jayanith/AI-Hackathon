<p align="center">
  <img src="https://img.shields.io/badge/Google%20Gemini-AI%20Powered-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini AI" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/Express-4-000000?style=for-the-badge&logo=express&logoColor=white" alt="Express" />
  <img src="https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/NetworkX-Graph%20Engine-orange?style=for-the-badge" alt="NetworkX" />
</p>

# 🛡️ TrustGraph AI

**Explainable, Multi-Agent, Graph-Aware Fraud Control Dashboard**

An end-to-end fraud detection and remediation platform that combines tabular ML scoring, graph-based collusion detection, and LLM-powered explanations — all orchestrated through a 3-agent pipeline with built-in fairness guardrails, livelihood protections, and an immutable audit trail.

> Built for the AI Hackathon — powered by the **Google Gemini API** (`@google/genai` SDK).

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Setup](#environment-setup)
  - [Running the Application](#running-the-application)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [3-Agent Orchestration Pipeline](#-3-agent-orchestration-pipeline)
- [Graph Anomaly Engine](#-graph-anomaly-engine)
- [Fairness & Governance](#-fairness--governance)
- [Testing](#-testing)
- [License](#-license)

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **3-Agent Multi-Agent Orchestration** | Risk scoring → Gemini AI explanation → Self-check compliance — each agent has one job and passes inspectable dictionaries to the next |
| **Graph Collusion Detection** | NetworkX-powered actor graph identifies shared device rings, IP subnet overlaps, and seller-buyer collusion networks |
| **Gemini AI Explanations** | Plain-language case explanations generated via Google Gemini 2.0 Flash for medium/high-risk cases (low-risk cases use free templates to minimize cost) |
| **Livelihood Guardrails & SLA** | Automatic 24h human review routing for high-impact payout holds — no hard suspensions unless model precision ≥ 95% |
| **Immutable Audit Trail** | Append-only audit log with timestamped events for every case review, appeal, and decision |
| **Appeal Workflow** | Sellers can submit appeals with email notifications and SLA-bound investigator review |
| **Real-Time Signal Verification** | IP reputation (AbuseIPDB), disposable email detection, and GSTIN format validation |
| **Fairness Monitoring** | Action-rate parity tracked across seller tenure and delivery partner cohorts with disparate impact warnings |
| **Elliptic Benchmark** | Graph anomaly technique validated against the real Elliptic Bitcoin dataset (30K labeled nodes) |
| **Cost Tracking** | Per-decision LLM cost monitoring with token-level granularity |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        React Dashboard (Vite)                       │
│   Cases Table │ Case Detail │ Fairness │ Audit Log │ Graph Stats    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ REST API
┌──────────────────────────────▼──────────────────────────────────────┐
│                    Express / TypeScript Server                      │
│              (server.ts — port 3000, Vite middleware)               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐   ┌──────────────────┐   ┌─────────────────────┐  │
│  │ Risk Agent   │──▶│ Explanation Agent │──▶│ Self-Check Agent    │  │
│  │ (Tabular +   │   │ (Gemini AI LLM)  │   │ (Policy Guardrails) │  │
│  │  Graph Score) │   └──────────────────┘   └─────────────────────┘  │
│  └─────────────┘                                                    │
│                                                                     │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Audit Trail     │  │ Cost Tracker │  │ External Signal APIs  │  │
│  │ (Append-only)   │  │ (Per-decision)│  │ (IP / Email / GSTIN) │  │
│  └─────────────────┘  └──────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
     IEEE-CIS Dataset   Elliptic Dataset   Live Signals
     (Fraud Labels)     (Graph Benchmark)  (AbuseIPDB)
```

---

## 🧰 Tech Stack

### Frontend
| Technology | Purpose |
|-----------|---------|
| **React 19** | UI framework |
| **Vite 8** | Build tool & dev server |
| **Lucide React** | Icon library |
| **CSS3** | Custom styling with glassmorphism & dark mode |

### Backend
| Technology | Purpose |
|-----------|---------|
| **Node.js + Express 4** | Primary API server |
| **TypeScript (tsx)** | Type-safe server runtime |
| **Google Gemini API** | LLM-powered case explanations (`@google/genai` SDK) |

### Python Backend (Optional)
| Technology | Purpose |
|-----------|---------|
| **FastAPI + Uvicorn** | Alternative REST API with full ML pipeline |
| **scikit-learn** | Random Forest tabular fraud model |
| **NetworkX** | Graph-based collusion scoring |
| **pandas / NumPy** | Data processing |

### LLM Provider Support
| Provider | Model | Priority |
|----------|-------|----------|
| **Google Gemini** ⭐ | `gemini-2.0-flash` / `gemini-2.0-flash-lite` | Primary |
| Groq | `llama-3.1-8b-instant` | Fallback 1 |
| Anthropic | `claude-3-haiku` | Fallback 2 |
| OpenAI | `gpt-4.1-mini` | Fallback 3 |

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** ≥ 18.x
- **npm** ≥ 9.x
- **Python** ≥ 3.10 *(only if running the FastAPI backend)*

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/trustgraph-ai.git
cd trustgraph-ai

# 2. Install Node.js dependencies
npm install
```

### Environment Setup

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required — Primary AI Engine
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Optional — Fallback LLM providers
GROQ_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Optional — External signal APIs
ABUSEIPDB_API_KEY=your_abuseipdb_key
DEBOUNCE_API_KEY=

# Optional — Email notifications
SENDGRID_API_KEY=
SENDGRID_SENDER_EMAIL=notifications@trustgraph.ai
```

> **Note:** The app runs in **demo mode** with rule-based explanations if no LLM API key is configured. All features remain functional.

### Running the Application

#### Full-Stack (Recommended)

```bash
npm run dev
```

This starts the Express + Vite dev server on **http://localhost:3000** — serving both the API and the React frontend.

#### Production Build

```bash
npm run build
npm start
```

#### Python FastAPI Backend (Optional)

If you want to run the full ML pipeline with scikit-learn and NetworkX:

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📡 API Reference

All endpoints are available at both `/api/<path>` and `/<path>`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check and system status |
| `GET` | `/api/cases` | List fraud cases (paginated via `?limit=50`) |
| `GET` | `/api/cases/:case_id` | Detailed case view with live AI explanation and signal lookups |
| `POST` | `/api/cases/:case_id/explain` | Generate/refresh Gemini AI explanation for a specific case |
| `POST` | `/api/cases/:case_id/appeal` | Submit seller appeal (logs to audit trail, sends notification) |
| `GET` | `/api/model/metrics` | Tabular model performance (AUC, precision, recall) |
| `GET` | `/api/fairness` | Fairness parity report across seller tenure & delivery partner cohorts |
| `GET` | `/api/audit` | Full immutable audit trail |
| `GET` | `/api/graph/summary` | NetworkX collusion graph statistics |
| `GET` | `/api/elliptic/metrics` | Elliptic Bitcoin dataset benchmark results |
| `GET` | `/api/cost/summary` | LLM cost tracker (calls, tokens, cost per decision) |
| `GET` | `/api/llm/status` | Configured LLM providers and usage stats |

### Example: Get Cases

```bash
curl http://localhost:3000/api/cases?limit=10
```

### Example: Submit Appeal

```bash
curl -X POST http://localhost:3000/api/cases/CASE-10492/appeal \
  -H "Content-Type: application/json" \
  -d '{"actor": "Seller A", "statement": "This transaction was legitimate", "actor_email": "seller@example.com"}'
```

---

## 📁 Project Structure

```
trustgraph-ai/
├── server.ts                 # Express + Vite full-stack server (primary)
├── index.html                # Root HTML entry point
├── vite.config.js            # Vite configuration
├── package.json              # Node.js dependencies & scripts
├── .env.example              # Environment variable template
├── metadata.json             # Project metadata
│
├── frontend/                 # React Frontend
│   ├── src/
│   │   ├── main.jsx          # React entry point
│   │   ├── App.jsx           # Main dashboard application (1400+ lines)
│   │   ├── App.css           # Component styles
│   │   └── index.css         # Global styles & design system
│   ├── package.json          # Frontend dependencies
│   └── vite.config.js        # Frontend Vite config
│
├── backend/                  # Python FastAPI Backend (optional)
│   ├── main.py               # FastAPI app with all endpoints
│   ├── agents.py             # 3-agent orchestration (Risk → Explanation → SelfCheck)
│   ├── model.py              # scikit-learn Random Forest model
│   ├── graph.py              # NetworkX collusion graph engine
│   ├── fairness.py           # Action-rate parity & disparate impact monitoring
│   ├── elliptic.py           # Elliptic Bitcoin dataset benchmark
│   ├── data.py               # IEEE-CIS dataset loader
│   ├── external_apis.py      # AbuseIPDB, email, GSTIN signal integrations
│   ├── cost_tracker.py       # Per-decision LLM cost accounting
│   ├── notifications.py      # SendGrid email notifications
│   └── requirements.txt      # Python dependencies
│
├── tests/                    # Test suite
│   ├── test_core.py          # Core functionality tests
│   ├── test_stage1.py        # Stage 1 tests
│   ├── test_stage2.py        # Stage 2 tests
│   └── test_stage3.py        # Stage 3 tests
│
└── trustgraph/               # Supporting modules
```

---

## 🤖 3-Agent Orchestration Pipeline

The system uses exactly **three cooperating agents** — plain Python/TypeScript classes, not a heavyweight agent framework. Each agent has one job and passes small, inspectable dictionaries to the next.

```
Transaction ──▶ [1] Risk Agent ──▶ [2] Explanation Agent ──▶ [3] Self-Check Agent ──▶ Decision
```

### Agent 1: Risk Agent
- Combines the **tabular ML score** (card type, email domain, seller tenure) with the **graph collusion score** (shared devices, IP overlaps, payout address matches)
- Weighted formula: `combined = 0.65 × tabular + 0.35 × graph`
- Outputs a risk tier: `LOW` (< 0.30) | `MEDIUM` (0.30–0.65) | `HIGH` (≥ 0.65)

### Agent 2: Explanation Agent
- **LOW risk:** Free template explanation (cost: $0)
- **MEDIUM/HIGH risk:** Calls Google Gemini API for a plain-language, 2–3 sentence explanation citing specific evidence
- Falls back through Groq → Claude → OpenAI → rule-based template if primary LLM is unavailable

### Agent 3: Self-Check Agent
- Enforces the **95% precision guardrail** — no hard action (suspension) unless model precision exceeds 95%
- **LOW:** No action, instant payout release
- **MEDIUM:** Soft intervention (step-up verification)
- **HIGH:** Temporary payout hold + routed to human investigator queue with 24h SLA

---

## 🔗 Graph Anomaly Engine

The graph engine uses **NetworkX** to build an actor-relationship graph from shared identifiers:

- **Nodes:** Sellers + shared identifiers (device IDs, IP addresses, payout addresses)
- **Edges:** Seller → identifier connections (deduplicated)
- **Scoring:** `0.4 × normalized_degree + 0.6 × normalized_shared_neighbours` (bounded to [0, 1])

This produces an **explainable collusion score** — not a black-box GNN — so investigators can trace exactly which shared identifiers triggered the flag.

The approach is validated against the **Elliptic Bitcoin dataset** (30,000 labeled nodes, Random Forest classifier achieving ~91% precision, ~84% recall, ~94.5% AUC).

---

## ⚖️ Fairness & Governance

The platform continuously monitors for **disparate impact** across:

1. **Seller Tenure Cohorts:** New sellers (< 90 days) vs. Established sellers (≥ 90 days)
2. **Delivery Partner Cohorts:** New partners (< 6 months) vs. Established partners

Key protections:
- Action-rate parity difference tracked in **percentage points**
- Automatic **disparate impact warning** if any cohort deviates > 5pp from baseline
- **Livelihood guardrails:** No automated hard action — all high-risk cases routed to human reviewers
- **Appeal workflow** with append-only audit trail and 24h SLA

---

## 🧪 Testing

```bash
# Run Python tests
python -m pytest tests/ -v
```

---

## 📄 License

This project was built for the AI Hackathon. See repository for license details.

---

<p align="center">
  Built with ❤️ using <strong>Google Gemini AI</strong> · React · Express · NetworkX
</p>
