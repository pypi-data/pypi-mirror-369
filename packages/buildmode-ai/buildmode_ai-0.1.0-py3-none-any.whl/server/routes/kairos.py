"""Routes for interacting with the Kairos agent."""

from fastapi import APIRouter
from pydantic import BaseModel

from server.agents.kairos import chat_agent


router = APIRouter(prefix="/kairos", tags=["kairos"])


class Prompt(BaseModel):
    """Schema for chat prompts."""

    prompt: str


@router.post("/chat")
async def chat(data: Prompt):
    """Chat with the Kairos agent."""

    reply = await chat_agent.run(data.prompt)
    return {"reply": reply}
