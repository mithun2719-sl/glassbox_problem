from config import TAVILY_API_KEY


def search_web(query: str) -> list[dict]:
    if not TAVILY_API_KEY:
        return []
    from tavily import TavilyClient
    return TavilyClient(api_key=TAVILY_API_KEY).search(query=query, max_results=3).get("results", [])
