from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse

from app.agents.chatbot import chat


router = APIRouter(
    prefix="/agents"
)


@router.get("/")
def read_items():
    return [
        {
            "name": "Chatbot",
            "description": "A chatbot agent that can answer single questions.",
        }
    ]

@router.get("/chatbot")
def read_chatbot(model: str, prompt: str, response: Response):
    return StreamingResponse(
        chat(prompt=prompt, model=model),
        media_type="text/event-stream"
    )

