from fastapi import APIRouter, HTTPException

from api.chat_schemas import (
    ChatRequest,
    ChatResponse,
)
from src.llm.chat import ask_narrate_iq


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
):

    try:

        conversation = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.conversation
        ]

        answer = ask_narrate_iq(
            question=request.question,
            conversation=conversation,
        )

        return ChatResponse(
            answer=answer
        )

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"LLM request failed: {exc}"
            ),
        ) from exc