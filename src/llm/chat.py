import json
from pathlib import Path

from src.llm.client import generate_response


DECISION_PATH = Path("data/processed/decision_object.json")


def load_decision() -> dict:
    if not DECISION_PATH.exists():
        raise FileNotFoundError(
            "decision_object.json not found. Run the analysis pipeline first."
        )

    return json.loads(DECISION_PATH.read_text(encoding="utf-8"))


def build_system_prompt(decision: dict) -> str:
    context = json.dumps(
        decision,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )

    return f"""
You are Narrate IQ, an evidence-grounded business intelligence assistant.

Use ONLY the supplied Narrate IQ decision context.

The deterministic analytics engine is the source of quantitative truth.
Never invent numbers, causes, business events, recommendations, or outcomes.
Distinguish evidence from causality. Preserve confidence levels.
If the requested information is unavailable, say so explicitly.
Prefer concise executive answers and use the actual values from the context.

CURRENT NARRATE IQ CONTEXT:
{context}
"""


def ask(question: str) -> str:
    question = question.strip()

    if not question:
        return "Please ask a business question."

    decision = load_decision()

    return generate_response(
        system_prompt=build_system_prompt(decision),
        user_prompt=question,
    )
