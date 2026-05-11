from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.chat_service import stream_response

router = APIRouter()


@router.post("/chat")
async def chat(payload: dict):
    message = payload.get("message", "")
    history = payload.get("history", [])
    mode = payload.get("mode", "regular")
    return StreamingResponse(
        stream_response(message, history, mode),
        media_type="text/plain",
    )
