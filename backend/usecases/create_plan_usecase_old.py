"""
Plan creation use case - orchestrates the business logic for creating new plans
"""
from typing import Dict, Any
from datetime import datetime
from bson import ObjectId
from fastapi import Depends

from models.domain import Plan
from repositories import PlanRepository
from usecases.create_plan_usecase_helper import CreatePlanUsecaseHelper

class CreatePlanUseCase:
    """Use case for creating new travel plans"""
    
    def __init__(self, 
                 plan_repository: PlanRepository = Depends(PlanRepository),
                 create_plan_helper: CreatePlanUsecaseHelper = Depends(CreatePlanUsecaseHelper)):
        self.plan_repository = plan_repository
        self.create_plan_helper = create_plan_helper
    
    async def execute(self, goal: str, description: str = None) -> Plan:
        """Execute the plan creation workflow"""
        
        # Step 1: Extract key information from the goal
        extracted_info = await self.create_plan_helper.extract_goal_info(goal)
        extracted_info["goal"] = goal  # Add the original goal for date calculation
        
        # Step 2: Gather external information
        external_info = await self.create_plan_helper.gather_external_info(extracted_info)
        
        # Step 3: Generate the plan using AI with today's date for context
        today = datetime.now()
        plan_data = await self.create_plan_helper.generate_plan_with_ai(goal, description, extracted_info, external_info, today)
        
        # Step 4: Enrich plan with external information and convert to domain model
        enriched_plan = await self.create_plan_helper.enrich_plan_with_external_data(plan_data, external_info, goal)
        
        # Step 5: Save to repository
        plan_dict = enriched_plan.dict()
        plan_id = await self.plan_repository.create(plan_dict)
        enriched_plan.id = plan_id
        
        return enriched_plan
    
    async def _extract_goal_info(self, goal: str) -> Dict[str, Any]:
        """Extract key information from the goal using AI"""
        return await self.ai_service.extract_goal_information(goal)
    
    async def _gather_external_info(self, extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Gather external information based on extracted goal info"""
        external_info = {}
        
        # Calculate trip dates based on the goal and current date
        today = datetime.now()
        duration = extracted_info.get("duration", 3)
        start_date, end_date = self._calculate_trip_dates(extracted_info.get("goal", ""), duration, today)
        
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
    
    def _calculate_trip_dates(self, goal: str, duration: int, today: datetime) -> tuple[datetime, datetime]:
        """Calculate actual trip start and end dates from goal and current date"""
        goal_lower = goal.lower()
        
        # Calculate start date based on goal keywords
        start_date = today
        
        # Handle specific timing keywords
        if "tomorrow" in goal_lower:
            start_date = today + timedelta(days=1)
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
    
    async def _generate_plan_with_ai(self, goal: str, description: str, extracted_info: Dict[str, Any], 
                                   external_info: Dict[str, Any], today: datetime) -> Dict[str, Any]:
        """Generate the main plan structure using AI"""
        return await self.ai_service.generate_plan_structure(goal, description, extracted_info, external_info, today)
    
    def _extract_day_weather_info(self, external_info: Dict[str, Any], day_date: str) -> list[Dict[str, Any]]:
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
    
    async def _enrich_plan_with_external_data(self, plan_data: Dict[str, Any], external_info: Dict[str, Any], goal: str) -> Plan:
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
                weather_info=self._extract_day_weather_info(external_info, day_data.get("date"))
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