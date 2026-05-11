import os
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent.parent / ".env"


def _load_config():
    if not _CONFIG_PATH.exists():
        return
    for line in _CONFIG_PATH.read_text().strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip()
        if key not in os.environ:
            os.environ[key] = val


_load_config()


def get_connection_params() -> dict:
    return {
        "server_hostname": os.environ.get("DATABRICKS_HOST"),
        "http_path": os.environ.get("DATABRICKS_HTTP_PATH"),
        "access_token": os.environ.get("DATABRICKS_TOKEN"),
    }


def query(sql: str) -> dict:
    params = get_connection_params()
    if not params["server_hostname"] or not params["http_path"] or not params["access_token"]:
        return {
            "error": "Databricks not configured. Set DATABRICKS_HOST, DATABRICKS_HTTP_PATH, and DATABRICKS_TOKEN in backend/.env"
        }

    try:
        from databricks import sql as dsql

        with dsql.connect(
            server_hostname=params["server_hostname"],
            http_path=params["http_path"],
            access_token=params["access_token"],
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                return {
                    "columns": columns,
                    "rows": [list(row) for row in rows],
                    "total": len(rows),
                }
    except ImportError:
        return {"error": "databricks-sql-connector not installed. Run: pip install databricks-sql-connector"}
    except Exception as e:
        return {"error": str(e)}


def get_schema() -> str:
    params = get_connection_params()
    if not params["server_hostname"] or not params["http_path"] or not params["access_token"]:
        return ""

    try:
        from databricks import sql as dsql

        with dsql.connect(
            server_hostname=params["server_hostname"],
            http_path=params["http_path"],
            access_token=params["access_token"],
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                schema_parts = []
                for t in tables:
                    db = t[0]
                    table_name = t[1]
                    cursor.execute(f"DESCRIBE {db}.{table_name}")
                    cols = cursor.fetchall()
                    col_lines = [f"  - {c[0]} ({c[1]})" for c in cols]
                    schema_parts.append(f"Table: {db}.{table_name}\n" + "\n".join(col_lines))
                return "\n\n".join(schema_parts) if schema_parts else "No tables found."
    except Exception as e:
        return f"Schema error: {e}"
