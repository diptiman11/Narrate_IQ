from fastapi import APIRouter, HTTPException

from api.chat_schemas import ChatRequest, ChatResponse
from src.llm.chat import ask


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        return {"answer": ask(request.question)}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"LLM request failed: {exc}",
        ) from exc
