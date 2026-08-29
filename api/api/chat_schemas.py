from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    conversation: list[ChatMessage] = []


class ChatResponse(BaseModel):
    answer: str