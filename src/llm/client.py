import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


def get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    return Groq(api_key=api_key)


def get_model() -> str:
    return os.getenv(
        "LLM_MODEL",
        "llama-3.3-70b-versatile",
    )


def generate_response(
    system_prompt: str,
    user_prompt: str,
) -> str:
    client = get_client()

    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content or ""
