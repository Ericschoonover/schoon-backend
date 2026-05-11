from fastapi import APIRouter
from services.ask_service import generate_answer

router = APIRouter()

@router.post("/ask")
async def ask(payload: dict):
    question = payload.get("question", "")
    answer = generate_answer(question)
    return {"answer": answer}
