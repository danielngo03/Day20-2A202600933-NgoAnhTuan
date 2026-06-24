"""Search client abstraction for ResearcherAgent."""

import json
import urllib.request
import urllib.parse
from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client using Wikipedia API."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
        
        try:
            # Step 1: Search Wikipedia for the query to get titles
            search_url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
                "action": "query",
                "list": "search",
                "srsearch": query,
                "utf8": "1",
                "format": "json",
                "srlimit": max_results
            })
            
            req = urllib.request.Request(
                search_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            )
            with urllib.request.urlopen(req) as response:
                search_data = json.loads(response.read().decode())
                
            results = []
            for item in search_data.get("query", {}).get("search", []):
                title = item["title"]
                snippet = item["snippet"].replace('<span class="searchmatch">', '').replace('</span>', '')
                
                # We could fetch the full page, but the snippet often contains good enough info for testing
                doc = SourceDocument(
                    title=title,
                    url=f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}",
                    snippet=snippet
                )
                results.append(doc)
            
            return results
        except Exception as e:
            # Fallback mock if network fails
            return [
                SourceDocument(
                    title="Mock Document",
                    url="https://mock.example.com/doc1",
                    snippet=f"This is a mock document for query: {query}. Error occurred during search: {e}"
                )
            ]
