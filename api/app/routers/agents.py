from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse

from app.agents.chatbot import chat
from app.agents.weather import ask_for_weather


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

@router.get("/weather")
def read_chatbot(model: str, prompt: str, response: Response):
    return StreamingResponse(
        ask_for_weather(prompt=prompt, model=model),
        media_type="text/event-stream"
    )

