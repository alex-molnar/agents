from fastapi import APIRouter, Depends, HTTPException

from app.agents.chatbot import chat


router = APIRouter(
    prefix="/agents"
)


fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("/")
def read_items():
    return [
        {
            "name": "Chatbot",
            "description": "A chatbot agent that can answer single questions.",
        }
    ]

@router.get("/chatbot")
def read_chatbot(model: str, prompt: str):
    return chat(prompt=prompt, model=model)

