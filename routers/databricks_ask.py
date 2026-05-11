from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.databricks_service import query, get_schema
from services.chat_service import get_client, get_system_prompt

router = APIRouter()

SQL_PROMPT = (
    "You are a SQL expert. Given the database schema below, generate a single SQL query "
    "that answers the user's question. Return ONLY the SQL query, nothing else.\n\n"
    "Schema:\n{schema}\n\n"
    "Question: {question}"
)

EXPLAIN_PROMPT = (
    "You are a professional data analyst. The user asked: {question}\n\n"
    "Here is the SQL that was run:\n{sql}\n\n"
    "Here are the results:\n{results}\n\n"
    "Explain the results clearly and concisely. Be direct, factual, and professional. "
    "Use the data to answer the question."
)


@router.post("/databricks/ask")
async def databricks_ask(payload: dict):
    question = payload.get("question", "")
    if not question.strip():
        return {"error": "Question is required"}

    try:
        client = get_client()
    except RuntimeError:
        return {"error": "API key not configured"}

    schema = get_schema()
    if not schema or schema.startswith("Schema error") or schema.startswith("No tables"):
        return {"error": schema or "Could not load database schema"}

    sql_prompt = SQL_PROMPT.format(schema=schema, question=question)
    sql_response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": sql_prompt}],
    )
    sql_query = sql_response.choices[0].message.content.strip()
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    if not sql_query.upper().startswith("SELECT"):
        return {"error": f"Could not generate valid SQL. Got: {sql_query}"}

    result = query(sql_query)
    if "error" in result:
        return {"error": result["error"], "sql": sql_query}

    results_text = f"Columns: {', '.join(result['columns'])}\n"
    for row in result["rows"][:20]:
        results_text += "\t".join(str(c) for c in row) + "\n"
    if result["total"] > 20:
        results_text += f"... and {result['total'] - 20} more rows\n"

    explain_prompt = EXPLAIN_PROMPT.format(question=question, sql=sql_query, results=results_text)
    context = f"{get_system_prompt('data')}\n\n{explain_prompt}"

    async def stream():
        stream_resp = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": context}],
            stream=True,
        )
        yield f"__SQL__\n{sql_query}\n__RESULTS__\n"
        for chunk in stream_resp:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    return StreamingResponse(stream(), media_type="text/plain")
