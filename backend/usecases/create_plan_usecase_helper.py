"""
Plan creation use case helper - contains helper functions for plan creation workflow
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import re
from bson import ObjectId
from fastapi import Depends
import logging

from services import WeatherService, WebSearchService, AIService
from models.domain import Plan, Day, Task, TaskStatus

class CreatePlanUsecaseHelper:
    """Helper class for plan creation use case"""
    
    def __init__(self, 
                 weather_service: WeatherService = Depends(WeatherService),
                 web_search_service: WebSearchService = Depends(WebSearchService),
                 ai_service: AIService = Depends(AIService)):
        self.weather_service = weather_service
        self.web_search_service = web_search_service
        self.ai_service = ai_service
        self.logger = logging.getLogger(__name__)
    
    async def extract_goal_info(self, goal: str) -> Dict[str, Any]:
        """Extract key information from the goal using AI"""
        self.logger.info(f"📊 Extracting information from goal: '{goal[:100]}...'")
        result = await self.ai_service.extract_goal_information(goal)
        self.logger.info(f"✅ Goal analysis complete - found {len(result)} attributes")
        return result
    
    def calculate_trip_dates(self, goal: str, duration: int, today: datetime) -> tuple[datetime, datetime]:
        """Calculate actual trip start and end dates from goal and current date"""
        goal_lower = goal.lower()
        
        # Calculate start date based on goal keywords
        start_date = today
        
        # First, try to parse specific dates (e.g., "25th oct", "23 sep", "december 15")
        specific_date = self._parse_specific_date(goal_lower, today)
        if specific_date:
            start_date = specific_date
        # Handle relative timing keywords
        elif "today" in goal_lower:
            start_date = today
        elif "tomorrow" in goal_lower:
            start_date = today + timedelta(days=1)
        elif "day after tomorrow" in goal_lower:
            start_date = today + timedelta(days=2)
        elif "next week" in goal_lower:
            # Next Monday
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:  # If today is Monday, go to next Monday
                days_until_monday = 7
            start_date = today + timedelta(days=days_until_monday)
        elif "next weekend" in goal_lower:
            # Next Saturday
            days_until_saturday = (5 - today.weekday()) % 7
            if days_until_saturday <= 0:  # If today is Saturday or Sunday, go to next Saturday
                days_until_saturday = 6 - today.weekday() + 7 if today.weekday() == 6 else 7 - today.weekday()
            start_date = today + timedelta(days=days_until_saturday)
        elif "this weekend" in goal_lower:
            # This coming Saturday
            days_until_saturday = (5 - today.weekday()) % 7
            if days_until_saturday == 0 and today.weekday() < 6:  # If today is Saturday
                start_date = today
            elif days_until_saturday <= 0:  # If today is Sunday, go to next Saturday
                days_until_saturday = 6
            start_date = today + timedelta(days=days_until_saturday)
        elif "next month" in goal_lower:
            # First weekend of next month
            next_month = today.replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)
            # Find first Saturday of next month
            days_until_saturday = (5 - next_month.weekday()) % 7
            start_date = next_month + timedelta(days=days_until_saturday)
        elif "in " in goal_lower:
            # Look for patterns like "in 3 days", "in 2 weeks", etc.
            match = re.search(r'in (\d+) (day|days|week|weeks)', goal_lower)
            if match:
                number = int(match.group(1))
                unit = match.group(2)
                if 'week' in unit:
                    start_date = today + timedelta(weeks=number)
                else:  # days
                    start_date = today + timedelta(days=number)
        else:
            # Default: Start in a few days to allow for planning
            start_date = today + timedelta(days=3)
        
        # Calculate end date
        end_date = start_date + timedelta(days=duration - 1)
        
        return start_date, end_date
    
    def _parse_specific_date(self, goal_lower: str, today: datetime) -> datetime | None:
        """Parse specific dates from goal text like '25th oct', '23 sep', 'december 15'"""
        import re
        from datetime import datetime
        
        # Common month abbreviations and names
        months = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        
        # Pattern 1: "25th oct", "23rd sep", "1st jan"
        pattern1 = re.search(r'(\d{1,2})(?:st|nd|rd|th)\s+([a-zA-Z]+)', goal_lower)
        if pattern1:
            day = int(pattern1.group(1))
            month_str = pattern1.group(2).lower()
            if month_str in months:
                month = months[month_str]
                year = today.year
                # If the date has passed this year, assume next year
                try:
                    target_date = datetime(year, month, day)
                    if target_date.date() < today.date():
                        target_date = datetime(year + 1, month, day)
                    return target_date
                except ValueError:
                    pass  # Invalid date
        
        # Pattern 2: "23 sep", "15 december"
        pattern2 = re.search(r'(\d{1,2})\s+([a-zA-Z]+)', goal_lower)
        if pattern2:
            day = int(pattern2.group(1))
            month_str = pattern2.group(2).lower()
            if month_str in months:
                month = months[month_str]
                year = today.year
                # If the date has passed this year, assume next year
                try:
                    target_date = datetime(year, month, day)
                    if target_date.date() < today.date():
                        target_date = datetime(year + 1, month, day)
                    return target_date
                except ValueError:
                    pass  # Invalid date
        
        # Pattern 3: "october 25", "december 15"
        pattern3 = re.search(r'([a-zA-Z]+)\s+(\d{1,2})', goal_lower)
        if pattern3:
            month_str = pattern3.group(1).lower()
            day = int(pattern3.group(2))
            if month_str in months:
                month = months[month_str]
                year = today.year
                # If the date has passed this year, assume next year
                try:
                    target_date = datetime(year, month, day)
                    if target_date.date() < today.date():
                        target_date = datetime(year + 1, month, day)
                    return target_date
                except ValueError:
                    pass  # Invalid date
        
        return None
    
    async def gather_external_info(self, extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Gather external information based on extracted goal info"""
        external_info = {}
        
        # Calculate trip dates based on the goal and current date
        today = datetime.now()
        duration = extracted_info.get("duration", 3)
        start_date, end_date = self.calculate_trip_dates(extracted_info.get("goal", ""), duration, today)
        
        # Store trip dates in external_info for later use
        external_info["trip_start_date"] = start_date
        external_info["trip_end_date"] = end_date
        external_info["trip_duration"] = duration
        
        # Get weather information for specific trip dates if destination is mentioned
        if extracted_info.get("destination"):
            destination = extracted_info["destination"]
            weather_data = await self.weather_service.get_weather_for_trip_dates(destination, start_date, end_date)
            external_info["weather"] = weather_data
        
        # Search for relevant information
        search_queries = []
        if extracted_info.get("destination"):
            search_queries.append(f"best places to visit in {extracted_info['destination']}")
            search_queries.append(f"restaurants in {extracted_info['destination']}")
        
        # Handle activities safely - ensure it's a list
        activities = extracted_info.get("activities", [])
        if activities and isinstance(activities, list):  # Only iterate if activities is a non-empty list
            for activity in activities:
                search_queries.append(f"{activity} in {extracted_info.get('destination', '')}")
        
        search_results = {}
        for query in search_queries[:3]:  # Limit to 3 searches
            results = await self.web_search_service.search(query, 3)
            search_results[query] = results
        
        external_info["search_results"] = search_results
        
        return external_info
    
    async def generate_plan_with_ai(self, goal: str, description: str, extracted_info: Dict[str, Any], 
                                   external_info: Dict[str, Any], today: datetime) -> Dict[str, Any]:
        """Generate the main plan structure using AI"""
        return await self.ai_service.generate_plan_structure(goal, description, extracted_info, external_info, today)
    
    def extract_day_weather_info(self, external_info: Dict[str, Any], day_date: str) -> List[Dict[str, Any]]:
        """Extract weather information for a specific day"""
        if not external_info.get("weather") or not day_date:
            return []
        
        weather_data = external_info["weather"]
        daily_forecasts = weather_data.get("daily_forecasts", [])
        
        # Find weather info for the specific date
        for day_weather in daily_forecasts:
            if day_weather.get("date") == day_date:
                weather_info = {
                    "date": day_weather.get("date"),
                    "day_name": day_weather.get("day_name"),
                    "min_temp": day_weather.get("min_temp"),
                    "max_temp": day_weather.get("max_temp"),
                    "avg_temp": day_weather.get("avg_temp"),
                    "condition": day_weather.get("condition"),
                    "description": day_weather.get("description"),
                    "rain_probability": day_weather.get("rain_probability"),
                    "humidity": day_weather.get("humidity"),
                    "wind_speed": day_weather.get("wind_speed"),
                    "weather_advisory": day_weather.get("weather_advisory"),
                    "data_source": day_weather.get("data_source"),
                    "season": day_weather.get("season"),
                    "weather_available": day_weather.get("weather_available", False)
                }
                return [weather_info]  # Return as a list
        
        # If no specific weather found, return basic info as a list
        basic_info = {
            "weather_source": weather_data.get("weather_source", "Unknown"),
            "forecast_available": weather_data.get("forecast_available", False)
        }
        return [basic_info]
    
    async def enrich_plan_with_external_data(self, plan_data: Dict[str, Any], external_info: Dict[str, Any], goal: str) -> Plan:
        """Enrich the plan with external information and convert to domain model"""
        
        # Convert to our Plan model
        days = []
        for day_data in plan_data.get("days", []):
            tasks = []
            for task_data in day_data.get("tasks", []):
                task = Task(
                    id=str(ObjectId()),  # Generate a proper ID for each task
                    title=task_data.get("title", ""),
                    description=task_data.get("description", ""),
                    estimated_duration=task_data.get("estimated_duration", ""),
                    status=TaskStatus(task_data.get("status", "pending")),
                    external_info={}
                )
                tasks.append(task)
            
            day = Day(
                day_number=day_data.get("day_number", 1),
                date=day_data.get("date"),
                tasks=tasks,
                summary=day_data.get("summary", ""),
                weather_info=self.extract_day_weather_info(external_info, day_data.get("date"))
            )
            days.append(day)
        
        plan = Plan(
            id=str(ObjectId()),  # Generate a proper ID for the plan
            goal=goal,  # Use the original goal parameter
            description=plan_data.get("description", ""),
            days=days,
            total_duration=plan_data.get("total_duration", "1 day")
        )
        
        return plan