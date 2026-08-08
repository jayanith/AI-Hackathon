"""The MVP has exactly three cooperating agents.

They are plain Python classes, not a heavyweight agent framework.  Each has one
job and passes small, inspectable dictionaries to the next agent.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import pandas as pd

from backend.model import ModelBundle, score_transactions
from backend import cost_tracker


@dataclass
class RiskAgent:
    """Combines the cheap tabular model with the local graph score."""

    model: ModelBundle

    def analyse(self, transaction: pd.Series) -> dict[str, Any]:
        base_score = float(score_transactions(self.model, pd.DataFrame([transaction]))["base_risk_score"].iloc[0])
        graph_score = float(transaction.get("graph_collusion_score", 0.0))
        combined_score = round(.65 * base_score + .35 * graph_score, 4)
        tier = "low" if combined_score < .30 else "medium" if combined_score < .65 else "high"
        return {
            "base_risk_score": base_score,
            "graph_collusion_score": graph_score,
            "combined_risk_score": combined_score,
            "risk_tier": tier,
            "graph_evidence": transaction.get("graph_evidence", "No graph evidence available"),
        }


class ExplanationAgent:
    """Calls an LLM only for medium/high cases; low risk uses a free template.
    
    Cost principle: LLM is expensive — only spend it where a human will act.
    LOW risk cases get a structured template (cost: $0).
    MEDIUM/HIGH cases get a real LLM explanation (cost: ~$0.0003/call).
    This keeps average cost-per-decision low while quality matters most.
    """

    def explain(self, transaction: pd.Series, risk: dict[str, Any], deferred: bool = False) -> dict[str, Any]:
        if risk["risk_tier"] == "low" or deferred:
            cost_tracker.record_case(llm_used=False)
            return {
                "summary": self._template(transaction, risk),
                "llm_used": False,
                "llm_status": "Skipped — low risk case (cost: $0)" if risk["risk_tier"] == "low" else "Deferred — load case detail for LLM explanation"
            }

        prompt = (
            "You are a fraud investigator writing a plain-language explanation for two audiences: "
            "(1) an investigator deciding whether to act, and (2) the seller who may appeal. "
            "Write 2-3 sentences. State the specific evidence — exact scores, identifier counts, shared links. "
            "Do not use jargon. Do not state fraud is proven. Do not mention protected traits. "
            "End with: 'A human reviewer will assess this case.'\n\n"
            f"Transaction ID: {transaction.get('TransactionID')}\n"
            f"Amount: ₹{transaction.get('TransactionAmt', 0):,.0f}\n"
            f"Risk tier: {risk['risk_tier'].upper()}\n"
            f"Tabular fraud score: {risk['base_risk_score']:.0%}"
            f" (card type, email domain, seller tenure)\n"
            f"Graph collusion score: {risk['graph_collusion_score']:.0%}\n"
            f"Graph evidence: {risk['graph_evidence']}"
        )

        # Try Gemini first (primary), then Groq, then Claude, then OpenAI, then template
        result = self._try_gemini(prompt, transaction, risk)
        if result and result.get('llm_used'):
            cost_tracker.record_case(llm_used=True)
            return result
        result = self._try_groq(prompt, transaction, risk)
        if result and result.get('llm_used'):
            cost_tracker.record_case(llm_used=True)
            return result
        result = self._try_claude(prompt, transaction, risk)
        if result and result.get('llm_used'):
            cost_tracker.record_case(llm_used=True)
            return result
        result = self._try_openai(prompt, transaction, risk)
        if result and result.get('llm_used'):
            cost_tracker.record_case(llm_used=True)
            return result

        cost_tracker.record_case(llm_used=False, failed=True)
        return {"summary": self._template(transaction, risk), "llm_used": False, "llm_status": "Rule-based explanation (LLM quota unavailable)"}

    def _try_groq(self, prompt: str, transaction: pd.Series, risk: dict[str, Any]) -> dict[str, Any] | None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None
        try:
            from groq import Groq
            model = "llama-3.1-8b-instant"
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                max_tokens=120,
                messages=[{"role": "user", "content": prompt}]
            )
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = cost_tracker.record_call(model, input_tokens, output_tokens)
            return {
                "summary": response.choices[0].message.content.strip(),
                "llm_used": True,
                "llm_model": model,
                "tokens": {"input": input_tokens, "output": output_tokens},
                "call_cost_usd": round(cost, 6),
            }
        except Exception as err:
            return {"summary": self._template(transaction, risk), "llm_used": False, "llm_error": str(err)[:120]}

    def _try_gemini(self, prompt: str, transaction: pd.Series, risk: dict[str, Any]) -> dict[str, Any] | None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            from google import genai
            from google.genai import types
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(max_output_tokens=120)
            )
            input_tokens = response.usage_metadata.prompt_token_count or 0
            output_tokens = response.usage_metadata.candidates_token_count or 0
            cost = cost_tracker.record_call(model_name, input_tokens, output_tokens)
            return {
                "summary": response.text.strip(),
                "llm_used": True,
                "llm_model": model_name,
                "tokens": {"input": input_tokens, "output": output_tokens},
                "call_cost_usd": round(cost, 6),
            }
        except Exception as err:
            return {"summary": self._template(transaction, risk), "llm_used": False, "llm_error": str(err)[:120]}

    def _try_claude(self, prompt: str, transaction: pd.Series, risk: dict[str, Any]) -> dict[str, Any] | None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        try:
            import anthropic
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model,
                max_tokens=120,
                messages=[{"role": "user", "content": prompt}]
            )
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = cost_tracker.record_call(model, input_tokens, output_tokens)
            return {
                "summary": response.content[0].text.strip(),
                "llm_used": True,
                "llm_model": model,
                "tokens": {"input": input_tokens, "output": output_tokens},
                "call_cost_usd": round(cost, 6),
            }
        except Exception as err:
            return {"summary": self._template(transaction, risk), "llm_used": False, "llm_error": str(err)[:120]}

    def _try_openai(self, prompt: str, transaction: pd.Series, risk: dict[str, Any]) -> dict[str, Any] | None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            from openai import OpenAI
            model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                max_tokens=120,
                messages=[{"role": "user", "content": prompt}]
            )
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = cost_tracker.record_call(model, input_tokens, output_tokens)
            return {
                "summary": response.choices[0].message.content.strip(),
                "llm_used": True,
                "llm_model": model,
                "tokens": {"input": input_tokens, "output": output_tokens},
                "call_cost_usd": round(cost, 6),
            }
        except Exception as err:
            return {"summary": self._template(transaction, risk), "llm_used": False, "llm_error": str(err)[:120]}

    @staticmethod
    def _template(transaction: pd.Series, risk: dict[str, Any]) -> str:
        tid = transaction.get('TransactionID')
        amt = transaction.get('TransactionAmt', 0)
        tier = risk['risk_tier'].upper()
        base = risk['base_risk_score']
        graph = risk['graph_collusion_score']
        evidence = risk['graph_evidence']

        if risk['risk_tier'] == 'high':
            return (
                f"Transaction {tid} (₹{amt:,.0f}) carries a {base:.0%} tabular fraud score driven by "
                f"card type, email domain, and seller tenure signals, combined with a {graph:.0%} network "
                f"collusion score from shared identifiers: {evidence}. "
                f"The combined {tier} risk score exceeds the action threshold. A human reviewer will assess this case."
            )
        if risk['risk_tier'] == 'medium':
            return (
                f"Transaction {tid} (₹{amt:,.0f}) shows a {base:.0%} tabular risk score and a {graph:.0%} "
                f"graph collusion score. Network links detected: {evidence}. "
                f"Step-up verification is recommended before processing. A human reviewer will assess this case."
            )
        return (
            f"Transaction {tid} (₹{amt:,.0f}) has a low combined risk score "
            f"(tabular {base:.0%}, graph {graph:.0%}). No significant network anomalies detected. "
            f"No action required at this time."
        )


class SelfCheckAgent:
    """Enforces the only hard-action rule before an action can be finalised."""

    def review(self, risk: dict[str, Any], model_metrics: dict[str, Any]) -> dict[str, str | bool]:
        if risk["risk_tier"] == "low":
            return {"proposed_action": "none", "final_action": "none", "human_review_required": False, "reason": "Low-risk case"}
        if risk["risk_tier"] == "medium":
            return {"proposed_action": "step-up verification", "final_action": "step-up verification", "human_review_required": False, "reason": "Soft intervention"}
        precision_is_safe = bool(model_metrics.get("hard_action_allowed")) and float(model_metrics.get("validation_precision", 0)) >= .95
        if precision_is_safe:
            return {"proposed_action": "temporary payout freeze", "final_action": "temporary payout freeze", "human_review_required": True, "reason": "95% precision guardrail met; appeal remains available"}
        return {"proposed_action": "temporary payout freeze", "final_action": "human review queue", "human_review_required": True, "reason": "Hard action blocked: 95% precision guardrail is not met"}


def run_three_agents(transaction: pd.Series, model: ModelBundle, deferred: bool = False) -> dict[str, Any]:
    """The only orchestration entry point: Risk -> Explanation -> Self-check."""
    risk = RiskAgent(model).analyse(transaction)
    explanation = ExplanationAgent().explain(transaction, risk, deferred=deferred)
    self_check = SelfCheckAgent().review(risk, model.metrics)
    return {"risk_agent": risk, "explanation_agent": explanation, "self_check_agent": self_check}
