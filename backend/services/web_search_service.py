"""
Web search service for external search API integration
"""
import requests
import os
from typing import Dict, Any, List

class WebSearchService:
    """Service for web search API integration"""
    
    def __init__(self):
        self.api_key = os.getenv("WEB_SEARCH_API_KEY")
        self.base_url = "https://serpapi.com/search"
    
    async def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search for information on the web"""
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                "engine": "google"
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            # Extract relevant information
            results = []
            if "organic_results" in data:
                for result in data["organic_results"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "link": result.get("link", ""),
                        "source": result.get("displayed_link", "")
                    })
            
            return {
                "query": query,
                "results": results,
                "total_results": len(results)
            }
        except Exception as e:
            print(f"Web search API error: {e}")
            return {"error": str(e), "results": []}
    
    async def search_multiple_queries(self, queries: List[str], results_per_query: int = 3) -> Dict[str, Any]:
        """Search multiple queries and return consolidated results"""
        all_results = {}
        
        for query in queries:
            results = await self.search(query, results_per_query)
            all_results[query] = results
        
        return all_results