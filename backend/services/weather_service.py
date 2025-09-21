"""
Weather service for external weather API integration
"""
import requests
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class WeatherService:
    """Service for weather API integration"""
    
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    async def get_weather_for_trip_dates(self, city: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get weather forecast specifically for trip dates with fallback for distant dates"""
        try:
            today = datetime.now()
            days_until_trip = (start_date - today).days
            duration = (end_date - start_date).days + 1
            
            # Check if trip is within the 5-day forecast window
            forecast_available = days_until_trip <= 5
            
            current_data = None
            forecast_data = None
            
            if forecast_available:
                # Get current weather and forecast for trips within 5 days
                current_data = await self._get_current_weather(city)
                forecast_data = await self._get_forecast(city)
            else:
                # For distant trips, only get current weather for location info
                current_data = await self._get_current_weather(city)
            
            # Process forecast data (real or seasonal estimates)
            daily_forecasts = self._process_forecast_for_dates(
                forecast_data, start_date, end_date, forecast_available, current_data
            )
            
            return {
                "current": current_data,
                "forecast": forecast_data,
                "daily_forecasts": daily_forecasts,
                "city": city,
                "trip_start": start_date.strftime("%Y-%m-%d"),
                "trip_end": end_date.strftime("%Y-%m-%d"),
                "trip_duration": duration,
                "days_until_trip": days_until_trip,
                "forecast_available": forecast_available,
                "weather_source": "OpenWeatherMap 5-day forecast" if forecast_available else "Seasonal estimates based on location"
            }
        except Exception as e:
            print(f"Weather API error: {e}")
            return {"error": str(e)}
    
    async def _get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city"""
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params)
        return response.json()
    
    async def _get_forecast(self, city: str) -> Dict[str, Any]:
        """Get 5-day forecast for a city"""
        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params)
        return response.json()
    
    def _process_forecast_for_dates(self, forecast_data: Dict, start_date: datetime, end_date: datetime, 
                                   forecast_available: bool, current_data: Dict = None) -> List[Dict]:
        """Process forecast data and generate weather info for trip dates"""
        daily_forecasts = []
        
        if forecast_available and forecast_data and "list" not in forecast_data:
            return daily_forecasts
        
        # Group forecasts by date (only if real forecast available)
        date_forecasts = {}
        if forecast_available and forecast_data and "list" in forecast_data:
            for item in forecast_data["list"]:
                forecast_date = datetime.fromtimestamp(item["dt"]).date()
                if forecast_date not in date_forecasts:
                    date_forecasts[forecast_date] = []
                date_forecasts[forecast_date].append(item)
        
        # Generate daily summaries for trip dates
        current_date = start_date.date()
        end_date_obj = end_date.date()
        
        while current_date <= end_date_obj:
            day_data = {
                "date": current_date.strftime("%Y-%m-%d"),
                "day_name": current_date.strftime("%A"),
                "weather_available": forecast_available and current_date in date_forecasts
            }
            
            if forecast_available and current_date in date_forecasts:
                # Use real forecast data
                day_forecasts = date_forecasts[current_date]
                
                # Calculate daily aggregates
                temps = [item["main"]["temp"] for item in day_forecasts]
                conditions = [item["weather"][0]["main"] for item in day_forecasts]
                descriptions = [item["weather"][0]["description"] for item in day_forecasts]
                
                # Find most common weather condition
                condition_counts = {}
                for condition in conditions:
                    condition_counts[condition] = condition_counts.get(condition, 0) + 1
                dominant_condition = max(condition_counts, key=condition_counts.get)
                
                # Check for rain
                rain_probability = 0
                total_rain = 0
                for item in day_forecasts:
                    if "rain" in item:
                        rain_probability = max(rain_probability, item.get("pop", 0) * 100)
                        total_rain += item["rain"].get("3h", 0)
                
                day_data.update({
                    "min_temp": round(min(temps), 1),
                    "max_temp": round(max(temps), 1),
                    "avg_temp": round(sum(temps) / len(temps), 1),
                    "condition": dominant_condition,
                    "description": descriptions[0],
                    "rain_probability": round(rain_probability),
                    "total_rain_mm": round(total_rain, 1),
                    "humidity": day_forecasts[0]["main"]["humidity"],
                    "wind_speed": day_forecasts[0]["wind"]["speed"],
                    "weather_advisory": self._generate_weather_advisory(dominant_condition, min(temps), max(temps), rain_probability),
                    "data_source": "5-day forecast"
                })
            else:
                # Use seasonal estimates for distant dates
                seasonal_data = self._generate_seasonal_weather_estimate(current_date, current_data)
                day_data.update(seasonal_data)
            
            daily_forecasts.append(day_data)
            current_date += timedelta(days=1)
        
        return daily_forecasts
    
    def _generate_seasonal_weather_estimate(self, date: datetime.date, current_data: Dict = None) -> Dict[str, Any]:
        """Generate seasonal weather estimates for dates beyond forecast range"""
        month = date.month
        
        # Get location info from current data if available
        location_lat = current_data.get("coord", {}).get("lat", 0) if current_data else 0
        location_lon = current_data.get("coord", {}).get("lon", 0) if current_data else 0
        
        # Determine hemisphere (rough approximation)
        is_northern_hemisphere = location_lat >= 0
        
        # Seasonal patterns based on month and hemisphere
        seasonal_data = self._get_seasonal_patterns(month, is_northern_hemisphere, location_lat)
        
        return {
            "min_temp": seasonal_data["min_temp"],
            "max_temp": seasonal_data["max_temp"],
            "avg_temp": seasonal_data["avg_temp"],
            "condition": seasonal_data["condition"],
            "description": seasonal_data["description"],
            "rain_probability": seasonal_data["rain_probability"],
            "humidity": seasonal_data["humidity"],
            "weather_advisory": seasonal_data["advisory"],
            "data_source": "Seasonal estimate (forecast unavailable)",
            "season": seasonal_data["season"]
        }
    
    def _get_seasonal_patterns(self, month: int, is_northern: bool, latitude: float) -> Dict[str, Any]:
        """Get seasonal weather patterns based on month, hemisphere, and latitude"""
        
        # Adjust seasons for hemisphere
        if is_northern:
            seasons = {
                12: "Winter", 1: "Winter", 2: "Winter",
                3: "Spring", 4: "Spring", 5: "Spring",
                6: "Summer", 7: "Summer", 8: "Summer",
                9: "Autumn", 10: "Autumn", 11: "Autumn"
            }
        else:
            seasons = {
                12: "Summer", 1: "Summer", 2: "Summer",
                3: "Autumn", 4: "Autumn", 5: "Autumn",
                6: "Winter", 7: "Winter", 8: "Winter",
                9: "Spring", 10: "Spring", 11: "Spring"
            }
        
        season = seasons[month]
        
        # Temperature adjustments based on latitude
        if abs(latitude) > 60:  # Arctic/Antarctic regions
            temp_modifier = -15
            humidity_base = 70
        elif abs(latitude) > 40:  # Temperate regions
            temp_modifier = 0
            humidity_base = 60
        elif abs(latitude) > 23:  # Subtropical regions
            temp_modifier = 10
            humidity_base = 65
        else:  # Tropical regions
            temp_modifier = 20
            humidity_base = 75
        
        # Base seasonal patterns
        seasonal_patterns = {
            "Winter": {
                "base_temp": 5 + temp_modifier,
                "temp_range": 8,
                "rain_prob": 40,
                "condition": "Clouds",
                "description": "overcast clouds",
                "advisory": "❄️ Winter season: Pack warm clothes and check for seasonal weather patterns"
            },
            "Spring": {
                "base_temp": 15 + temp_modifier,
                "temp_range": 12,
                "rain_prob": 50,
                "condition": "Rain",
                "description": "light rain",
                "advisory": "🌸 Spring season: Variable weather, pack layers and rain protection"
            },
            "Summer": {
                "base_temp": 25 + temp_modifier,
                "temp_range": 10,
                "rain_prob": 30,
                "condition": "Clear",
                "description": "clear sky",
                "advisory": "☀️ Summer season: Expect warm weather, pack sun protection"
            },
            "Autumn": {
                "base_temp": 18 + temp_modifier,
                "temp_range": 10,
                "rain_prob": 45,
                "condition": "Clouds",
                "description": "scattered clouds",
                "advisory": "🍂 Autumn season: Cool and variable weather, pack layers"
            }
        }
        
        pattern = seasonal_patterns[season]
        min_temp = pattern["base_temp"] - pattern["temp_range"] // 2
        max_temp = pattern["base_temp"] + pattern["temp_range"] // 2
        
        return {
            "season": season,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "avg_temp": pattern["base_temp"],
            "condition": pattern["condition"],
            "description": pattern["description"],
            "rain_probability": pattern["rain_prob"],
            "humidity": humidity_base,
            "advisory": pattern["advisory"]
        }
    
    def _generate_weather_advisory(self, condition: str, min_temp: float, max_temp: float, rain_probability: float) -> str:
        """Generate weather advisory for activity planning"""
        advisories = []
        
        # Temperature advisories
        if max_temp > 40:
            advisories.append("🌡️ EXTREME HEAT: Plan indoor activities during midday (11 AM - 4 PM)")
        elif max_temp > 35:
            advisories.append("☀️ Very hot day: Prefer early morning and evening outdoor activities")
        elif max_temp < 5:
            advisories.append("❄️ Very cold: Layer clothing and prefer heated indoor venues")
        elif min_temp < 0:
            advisories.append("🧊 Freezing temperatures: Check for ice and dress warmly")
        
        # Rain advisories
        if rain_probability > 70:
            advisories.append("🌧️ High rain probability: Prioritize indoor activities or covered venues")
        elif rain_probability > 40:
            advisories.append("☔ Possible rain: Have indoor backup plans ready")
        
        # Weather condition advisories
        if condition.lower() in ["thunderstorm", "storm"]:
            advisories.append("⛈️ STORM WARNING: Stay indoors during storm periods")
        elif condition.lower() == "snow":
            advisories.append("🌨️ Snow expected: Check travel conditions and dress warmly")
        elif condition.lower() == "fog":
            advisories.append("🌫️ Foggy conditions: Allow extra travel time and check visibility")
        
        if not advisories:
            if 15 <= max_temp <= 30 and rain_probability < 30:
                advisories.append("☀️ Great weather for outdoor activities!")
            else:
                advisories.append("🌤️ Pleasant weather for most activities")
        
        return " | ".join(advisories)