import requests
import os
from typing import Dict, Any, Optional
import json

class WeatherAPI:
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    async def get_weather(self, city: str, days: int = 3) -> Dict[str, Any]:
        """Get weather forecast for a city"""
        try:
            # Get current weather
            current_url = f"{self.base_url}/weather"
            current_params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            current_response = requests.get(current_url, params=current_params)
            current_data = current_response.json()
            
            # Get forecast (5-day forecast)
            forecast_url = f"{self.base_url}/forecast"
            forecast_params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            forecast_response = requests.get(forecast_url, params=forecast_params)
            forecast_data = forecast_response.json()
            
            return {
                "current": current_data,
                "forecast": forecast_data,
                "city": city
            }
        except Exception as e:
            print(f"Weather API error: {e}")
            return {"error": str(e)}

class WebSearchAPI:
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
