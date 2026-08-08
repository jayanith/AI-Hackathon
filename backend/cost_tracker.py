"""Running cost tracker for LLM explanation calls.

Pricing (as of 2025):
  Claude claude-haiku-3-5: input $0.80/1M tokens, output $4.00/1M tokens
  GPT-4.1-mini:            input $0.40/1M tokens, output $1.60/1M tokens
"""
from __future__ import annotations
import threading
from typing import Any

# Per-token costs in USD
PRICING: dict[str, dict[str, float]] = {
    "claude-haiku-3-5":        {"input": 0.80 / 1_000_000, "output": 4.00 / 1_000_000},
    "claude-3-haiku-20240307": {"input": 0.25 / 1_000_000, "output": 1.25 / 1_000_000},
    "gpt-4.1-mini":            {"input": 0.40 / 1_000_000, "output": 1.60 / 1_000_000},
    "gpt-4o-mini":             {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
    "gemini-1.5-flash":        {"input": 0.00 / 1_000_000, "output": 0.00 / 1_000_000},
    "gemini-2.0-flash-lite":   {"input": 0.00 / 1_000_000, "output": 0.00 / 1_000_000},
    "llama-3.1-8b-instant":    {"input": 0.00 / 1_000_000, "output": 0.00 / 1_000_000},
}
DEFAULT_COST_PER_CALL = 0.0004  # fallback if model unknown

_lock = threading.Lock()
_state: dict[str, Any] = {
    "llm_calls": 0,
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "total_cost_usd": 0.0,
    "total_cases_processed": 0,  # includes free low-risk cases
    "failures": 0,
}


def record_call(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = PRICING.get(model, {})
    cost = (
        input_tokens  * pricing.get("input",  DEFAULT_COST_PER_CALL / 2) +
        output_tokens * pricing.get("output", DEFAULT_COST_PER_CALL / 2)
    )
    with _lock:
        _state["llm_calls"] += 1
        _state["total_input_tokens"] += input_tokens
        _state["total_output_tokens"] += output_tokens
        _state["total_cost_usd"] += cost
    return cost


def record_case(llm_used: bool = False, failed: bool = False) -> None:
    with _lock:
        _state["total_cases_processed"] += 1
        if failed:
            _state["failures"] += 1


def summary() -> dict[str, Any]:
    with _lock:
        s = dict(_state)
    total = s["total_cases_processed"]
    avg_usd = s["total_cost_usd"] / total if total > 0 else 0.0
    avg_inr = avg_usd * 84  # approximate USD→INR
    return {
        "llm_calls": s["llm_calls"],
        "total_cases_processed": total,
        "total_cost_usd": round(s["total_cost_usd"], 6),
        "avg_cost_per_decision_usd": round(avg_usd, 6),
        "avg_cost_per_decision_inr": round(avg_inr, 4),
        "total_input_tokens": s["total_input_tokens"],
        "total_output_tokens": s["total_output_tokens"],
        "failures": s["failures"],
    }
