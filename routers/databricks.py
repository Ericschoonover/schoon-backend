from fastapi import APIRouter
from services.databricks_service import query

router = APIRouter()


@router.post("/databricks/query")
async def run_query(payload: dict):
    sql = payload.get("sql", "")
    if not sql.strip():
        return {"error": "SQL query is required"}
    result = query(sql)
    return result
