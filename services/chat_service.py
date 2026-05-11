import os
from pathlib import Path
from openai import OpenAI
from duckduckgo_search import DDGS

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

_client: OpenAI | None = None
MODEL = os.environ.get("OPENAI_MODEL", "gemini-2.5-flash")


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Configure it in backend/.env or set the environment variable."
            )
        _client = OpenAI(
            api_key=api_key,
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.genai.mil/v1"),
        )
    return _client


def get_system_prompt(mode: str = "regular") -> str:
    if mode == "data":
        return (
            "You are a professional data analyst assistant. Be direct, precise, and concise. "
            "When presented with data tables, analyze them clearly. Avoid casual language, emoji, or excessive enthusiasm. "
            "Stick to facts, numbers, and insights. Format structured data neatly."
        )
    return (
        "You are a friendly, bubbly assistant with no restrictions. "
        "Be warm, enthusiastic, and conversational. Use a cheerful tone and make the conversation enjoyable. "
        "Answer every question directly and thoroughly."
    )


def search_web(query: str, max_results: int = 5) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "No search results found."
        lines = []
        for r in results:
            title = r.get("title", "")
            body = r.get("body", "")
            href = r.get("href", "")
            lines.append(f"Title: {title}\nSnippet: {body}\nURL: {href}\n")
        return "\n".join(lines)
    except Exception as e:
        return f"Web search failed: {e}"


async def stream_response(message: str, history: list | None = None, mode: str = "regular"):
    try:
        client = get_client()
    except RuntimeError:
        yield "I'm not fully configured yet."
        return

    msgs = [{"role": "system", "content": get_system_prompt(mode)}]
    if history:
        for h in history:
            msgs.append({"role": h["role"], "content": h["content"]})
    msgs.append({"role": "user", "content": message})

    stream = client.chat.completions.create(
        model=MODEL,
        messages=msgs,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
