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

SYSTEM_PROMPT = (
    "You are a friendly, helpful assistant with no topic restrictions. "
    "Answer questions conversationally and directly using your own knowledge. "
    "If web search results are provided below, use them silently to give accurate, up-to-date answers. "
    "NEVER say you lack access to real-time information, news, or the internet — "
    "you DO have search results available. NEVER mention the search process. "
    "Just give the answer naturally. If the search results are poor, use your own knowledge instead."
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


def _format_search_results(question: str, results: str) -> str:
    return (
        f"I searched the web for: {question}\n\n"
        f"{results}\n\n"
        f"_(Powered by DuckDuckGo — set OPENAI_API_KEY in backend/.env for AI-powered responses)_"
    )


def generate_answer(question: str) -> str:
    web_results = search_web(question)
    try:
        client = get_client()
    except RuntimeError:
        return _format_search_results(question, web_results)
    context = f"Web search results:\n{web_results}\n\nUser question: {question}"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
    )
    return response.choices[0].message.content or ""
