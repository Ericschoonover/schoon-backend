from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers correctly (import the FILE, not the package)
from routers.ingest import router as ingest_router
from routers.ask import router as ask_router
from routers.chat import router as chat_router
from routers.documents import router as documents_router
from routers.databricks import router as databricks_router
from routers.databricks_ask import router as databricks_ask_router

app = FastAPI()

# CORS so frontend can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(ingest_router, prefix="/api")
app.include_router(ask_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(databricks_router, prefix="/api")
app.include_router(databricks_ask_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "backend running", "message": "SCHOON API online"}
