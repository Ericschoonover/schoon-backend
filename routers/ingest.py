from fastapi import APIRouter, UploadFile, File
from services.ingest_service import process_file

router = APIRouter()

@router.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    result = await process_file(file)
    return {"status": "success", "details": result}
