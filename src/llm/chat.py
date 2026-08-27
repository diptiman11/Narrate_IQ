import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parents[2]

DECISION_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "decision_object.json"
)

load_dotenv(
    BASE_DIR / ".env"
)

GROQ_BASE_URL = (
    "https://api.groq.com/openai/v1"
)

DEFAULT_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b",
)


def load_decision_context() -> dict[str, Any]:

    if not DECISION_PATH.exists():
        raise FileNotFoundError(
            "decision_object.json not found. "
            "Run the Narrate IQ pipeline first."
        )

    with DECISION_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def build_system_prompt(
    context: dict[str, Any],
) -> str:

    context_json = json.dumps(
        context,
        indent=2,
        ensure_ascii=False,
    )

    return f"""
You are the Narrate IQ Business Intelligence Copilot.

Use ONLY the supplied Narrate IQ context.

Never invent:
- metrics
- causes
- events
- recommendations
- experiment outcomes
- learning results

Do not claim causation unless the evidence explicitly
supports causation.

Always preserve the numbers in the context.

When evidence is weak, say so.

When information is unavailable, say:

"That information is not available in the current
Narrate IQ analysis."

Prefer this structure when useful:

What happened?
Why?
Where?
What should we do?
What did we learn?

Always finish with:

Evidence:
- relevant evidence
- relevant metric
- relevant validation

CURRENT NARRATE IQ CONTEXT:

{context_json}
"""


def ask_narrate_iq(
    question: str,
    conversation: list[dict[str, str]] | None = None,
) -> str:

    question = question.strip()

    if not question:
        return (
            "Please enter a business question."
        )

    context = load_decision_context()

    api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. "
            "Add it to .env or the environment."
        )

    client = OpenAI(
        api_key=api_key,
        base_url=GROQ_BASE_URL,
    )

    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": build_system_prompt(
                context
            ),
        }
    ]

    if conversation:

        for message in conversation:

            role = message.get("role")
            content = message.get("content")

            if role not in {
                "user",
                "assistant",
            }:
                continue

            if not content:
                continue

            messages.append(
                {
                    "role": role,
                    "content": content,
                }
            )

    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=800,
    )

    answer = response.choices[0].message.content

    if not answer:
        return (
            "I could not generate an answer from "
            "the current Narrate IQ evidence."
        )

    return answer