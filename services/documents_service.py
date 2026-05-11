import os
import mimetypes

UPLOAD_DIR = "uploads"


def list_documents():
    if not os.path.isdir(UPLOAD_DIR):
        return []
    docs = []
    for fname in os.listdir(UPLOAD_DIR):
        fpath = os.path.join(UPLOAD_DIR, fname)
        if os.path.isfile(fpath):
            docs.append({
                "id": fname,
                "filename": fname,
                "size": os.path.getsize(fpath),
            })
    return docs


def get_document(doc_id: str):
    fpath = os.path.join(UPLOAD_DIR, doc_id)
    if not os.path.isfile(fpath):
        return None
    with open(fpath, "rb") as f:
        content = f.read()
    text = content.decode("utf-8", errors="replace")
    mime, _ = mimetypes.guess_type(fpath)
    return {
        "id": doc_id,
        "filename": doc_id,
        "text": text,
        "type": mime or "application/octet-stream",
    }


def get_file_path(doc_id: str):
    fpath = os.path.join(UPLOAD_DIR, doc_id)
    if os.path.isfile(fpath):
        return fpath
    return None
