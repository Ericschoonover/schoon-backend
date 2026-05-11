from fastapi import APIRouter
from fastapi.responses import FileResponse
from services.documents_service import list_documents, get_document, get_file_path

router = APIRouter()


@router.get("/documents")
def list_all():
    return list_documents()


@router.get("/documents/{doc_id}")
def detail(doc_id: str):
    doc = get_document(doc_id)
    if doc is None:
        return {"error": "not found"}, 404
    return doc


@router.get("/files/{doc_id}")
def serve_file(doc_id: str):
    fpath = get_file_path(doc_id)
    if fpath is None:
        return {"error": "not found"}, 404
    return FileResponse(fpath)
