import google.generativeai as genai
import os
from typing import List, Dict, Any
import json
from bson import ObjectId
from datetime import datetime
from external_apis import WeatherAPI, WebSearchAPI
from models import Plan, Day, Task, TaskStatus

class TaskPlanningAgent:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.weather_api = WeatherAPI()
        self.web_search = WebSearchAPI()
    
    async def generate_plan(self, goal: str, description: str = None) -> Plan:
        """Generate a comprehensive task plan from a natural language goal"""
        
        # Step 1: Extract key information from the goal
        extracted_info = await self._extract_goal_info(goal)
        
        # Step 2: Gather external information
        external_info = await self._gather_external_info(extracted_info)
        
        # Step 3: Generate the plan using Gemini with today's date for context
        today = datetime.now()
        plan_data = await self._generate_plan_with_gemini(goal, description, extracted_info, external_info, today)
        
        # Step 4: Enrich tasks with external information
        enriched_plan = await self._enrich_plan_with_external_data(plan_data, external_info, goal)
        
        return enriched_plan
    
    async def _extract_goal_info(self, goal: str) -> Dict[str, Any]:
        """Extract key information from the goal using Gemini"""
        prompt = f"""
        Analyze this goal and extract key information in JSON format:
        Goal: "{goal}"
        
        Extract:
        - destination (if travel-related)
        - duration (number of days as integer - if not explicitly mentioned, infer based on context):
          * Weekend: 2-3 days (return 3)
          * Week: 7 days (return 7)
          * Quick/short: 1-2 days (return 2)
          * Vacation/holiday: 5-7 days (return 7)
          * Long/extended: 7+ days (return 7 or higher)
        - activities (list of main activities)
        - preferences (any specific preferences mentioned)
        - budget_considerations (if mentioned)
        - time_of_year (if mentioned)
        
        DURATION INFERENCE RULES:
        - If user mentions "weekend": return 3
        - If user mentions "week": return 7
        - If user mentions "quick", "short", "brief", "day trip": return 2
        - If user mentions "vacation", "holiday", "getaway": return 7
        - If user mentions "long", "extended", "comprehensive": return 10
        - If user mentions specific numbers: use that exact number
        - If user mentions relative dates like "next weekend", "next week": calculate appropriate duration
        - If many activities mentioned: increase duration accordingly
        - Default for unspecified trips: return 3
        
        Return only valid JSON. Use empty strings for missing text fields and empty arrays for missing list fields.
        """
        
        response = None  # Initialize response variable
        try:
            response = self.model.generate_content(prompt)
            print(f"Raw response: {response}")
            print(f"Response text: '{response.text}'")
            print(f"Response text length: {len(response.text) if response.text else 'None'}")
            
            if not response.text or response.text.strip() == "":
                print("Empty response from Gemini API")
                return {"destination": "", "duration": 3, "activities": [], "preferences": [], "budget_considerations": "", "time_of_year": ""}
            
            # Clean the response text - remove markdown code blocks if present
            clean_text = response.text.strip()
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]  # Remove ```json
            if clean_text.startswith('```'):
                clean_text = clean_text[3:]   # Remove ```
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]  # Remove ending ```
            clean_text = clean_text.strip()
            
            print(f"Cleaned text: '{clean_text[:100]}...'")
            extracted = json.loads(clean_text)
            
            # Parse duration safely - handle both numbers and strings like "7+"
            duration_value = extracted.get("duration", 3)
            if isinstance(duration_value, str):
                # Handle strings like "7+", "5-7", etc.
                import re
                # Extract the first number from the string
                numbers = re.findall(r'\d+', str(duration_value))
                if numbers:
                    duration_value = int(numbers[0])
                else:
                    duration_value = 3  # Default fallback
            elif not isinstance(duration_value, int):
                duration_value = 3  # Default for any other type
            
            # Ensure minimum 1 day
            duration_value = max(1, duration_value)
            
            # Clean up null values and ensure proper types with improved defaults
            cleaned_extracted = {
                "destination": extracted.get("destination") or "",
                "duration": duration_value,
                "activities": extracted.get("activities") or [],
                "preferences": extracted.get("preferences") or [],
                "budget_considerations": extracted.get("budget_considerations") or "",
                "time_of_year": extracted.get("time_of_year") or ""
            }
            
            return cleaned_extracted
        except Exception as e:
            print(f"Error extracting goal info: {e}")
            print(f"Response was: {getattr(response, 'text', 'No response object') if response else 'No response object'}")
            return {"destination": "", "duration": 3, "activities": [], "preferences": [], "budget_considerations": "", "time_of_year": ""}
    
    async def _gather_external_info(self, extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Gather external information based on extracted goal info"""
        external_info = {}
        
        # Get weather information if destination is mentioned
        if extracted_info.get("destination"):
            destination = extracted_info["destination"]
            weather_data = await self.weather_api.get_weather(destination, extracted_info.get("duration", 3))
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
            results = await self.web_search.search(query, 3)
            search_results[query] = results
        
        external_info["search_results"] = search_results
        
        return external_info
    
    async def _generate_plan_with_gemini(self, goal: str, description: str, extracted_info: Dict[str, Any], external_info: Dict[str, Any], today: datetime) -> Dict[str, Any]:
        """Generate the main plan structure using Gemini"""
        
        # Prepare context for the LLM
        today_str = today.strftime("%A, %B %d, %Y")
        context = f"""
        Goal: {goal}
        Description: {description or "No additional description provided"}
        Today's Date: {today_str}
        
        Extracted Information:
        - Destination: {extracted_info.get('destination', 'Not specified')}
        - Duration: {extracted_info.get('duration', 1)} days
        - Activities: {', '.join(str(x) for x in extracted_info.get('activities', []))}
        - Preferences: {', '.join(str(x) for x in extracted_info.get('preferences', []))}
        
        External Information Available:
        - Weather data: {'Yes' if external_info.get('weather') else 'No'}
        - Web search results: {len(external_info.get('search_results', {}))} queries
        """
        
        prompt = f"""
        {context}
        
        Create a detailed day-by-day travel plan for this goal. 
        
        IMPORTANT: Calculate the actual dates based on today's date ({today_str}) and the user's request in the goal. 
        For example:
        - "next week" means starting 7 days from today
        - "next weekend" means the upcoming Saturday 
        - "next to next weekend" means the Saturday after next weekend
        - "tomorrow" means the day after today
        - If no specific date is mentioned, assume they want to start in a few days to a week
        
        Return a JSON structure with this exact format:
        {{
            "description": "Brief description of the overall plan",
            "total_duration": "X days",
            "days": [
                {{
                    "day_number": 1,
                    "date": "YYYY-MM-DD",
                    "summary": "Brief summary of day 1",
                    "tasks": [
                        {{
                            "title": "Task title",
                            "description": "Detailed task description with exact locations and addresses when possible",
                            "estimated_duration": "X hours",
                            "status": "pending"
                        }}
                    ]
                }}
        }}
        
        🚨 CRITICAL TRAVEL PLANNING REQUIREMENTS:
        
        1. **ARRIVAL & ACCOMMODATION PRIORITY:**
           - FIRST task must be arrival (airport/train station pickup)
           - SECOND task must be hotel check-in near major attractions
           - Choose hotel location strategically - close to most places you'll visit
           - Include exact hotel recommendations with area names
        
        2. **WEATHER-SMART PLANNING:**
           - If rainy/stormy weather predicted: prioritize INDOOR activities (museums, shopping malls, covered markets, restaurants)
           - If very hot (>40°C): plan early morning and evening outdoor activities, midday indoor activities
           - If very cold or extreme weather: add weather warnings and suggest alternative indoor options
           - ALWAYS mention weather impact: "Note: Due to rain forecast, this is an indoor alternative to outdoor sightseeing"
        
        3. **FUEL-EFFICIENT ROUTE OPTIMIZATION:**
           - Plan routes in geographical clusters to minimize travel time and fuel
           - Start with places NEAR the hotel
           - Then gradually move to FARTHER places
           - End the day back NEAR the hotel
           - NEVER zigzag between far and near places repeatedly
           - Group nearby attractions together in the same time slot
        
        4. **LOGICAL GEOGRAPHICAL PROGRESSION:**
           - Morning: Start with closest attractions to hotel (walking distance if possible)
           - Mid-day: Move to medium-distance attractions
           - Afternoon: Visit the farthest attractions
           - Evening: Return towards hotel area for dinner and rest
           - Include estimated travel times between locations
        
        5. **PRACTICAL TRAVEL DETAILS:**
           - Include specific addresses and landmark references
           - Mention transportation mode (walk, taxi, metro, bus)
           - Add buffer time for travel delays
           - Include meal breaks near the areas you're visiting (not random locations)
           - Suggest restaurants/cafes in the same vicinity as attractions
        
        6. **WEATHER ADVISORY SYSTEM:**
           - If extreme weather conditions exist, start with: "⚠️ WEATHER ADVISORY: [condition] - Consider rescheduling this trip for better weather"
           - But still provide the complete itinerary with indoor alternatives
           - Rate each day's weather suitability (1-10 scale)
        
        7. **TIME OPTIMIZATION:**
           - Account for opening/closing hours of attractions
           - Avoid travel during peak traffic hours when possible
           - Plan lunch near midday attractions, dinner near evening locations
           - Include realistic time estimates including queue/waiting times
        
        8. **INTELLIGENT ACTIVITY PLANNING BY TIME DURATION:**
           - Plan activities based on how long each activity actually takes, not arbitrary daily limits
           - Major attractions (museums, forts, palaces): 2-4 hours each
           - Medium activities (markets, temples, gardens): 1-2 hours each
           - Quick activities (cafes, viewpoints, short walks): 30min-1hr each
           - Full day activities (safari, trekking, day tours): Entire day
           - Calculate total time: Activities + Travel + Meals + Rest = Should not exceed 12-14 hours
           - Example day: Major attraction (3hrs) + Travel (1hr) + Lunch (1hr) + Medium attraction (2hrs) + Travel (30min) + Quick cafe (1hr) + Dinner (1hr) = 9.5hrs ✅
           - Bad example: 3 Major attractions (12hrs) + Travel (3hrs) + Meals (2hrs) = 17hrs ❌
           - SMART LOGIC: If you plan 1 museum (3hrs), you still have 9-11 hours left for other activities
           - SMART LOGIC: If you plan 3 museums (12hrs), you have no time left for anything else
           - Include travel time between locations (30min-2hours depending on distance)
           - Allow time for rest, meals, and unexpected delays
           - Quality over quantity - better to enjoy fewer places than rush through many
        
        EXAMPLE GOOD ROUTE: Hotel → Walk to nearby temple → Taxi to city palace (same area) → Lunch nearby → Afternoon visit to fort (farther) → Evening market (on way back) → Dinner near hotel
        
        EXAMPLE BAD ROUTE: Hotel → Far fort → Back to nearby temple → Far palace → Back to nearby market → Far restaurant
        
        Requirements:
        - Create exactly {extracted_info.get('duration', 1)} days
        - Plan activities based on realistic time requirements and do the math:
          * Major attractions (museums, forts, palaces): 2-4 hours each
          * Medium activities (markets, temples, gardens): 1-2 hours each  
          * Quick activities (cafes, viewpoints): 30min-1hr each
          * Full day activities (safari, trekking): Entire day
        - Total daily time should not exceed 12-14 hours (including travel, meals, rest)
        - USE MATH: Add up all activity durations + travel time + meal time = should fit in 12-14 hours
        - Include specific times, locations, and addresses when possible
        - Consider the activities and preferences mentioned
        - Make tasks actionable and specific with clear directions
        - Include realistic travel times between locations (30min-2hrs)
        - Optimize routes for minimal backtracking
        - Account for weather conditions and suggest alternatives
        - Prioritize arrival logistics and smart hotel location
        - Focus on quality experiences over quantity of places
        - LET THE TIME MATH DETERMINE NUMBER OF ACTIVITIES, NOT PRE-SET LIMITS
        
        Return only valid JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            print(f"Plan generation raw response: {response}")
            print(f"Plan generation response text: '{response.text}'")
            print(f"Plan generation response text length: {len(response.text) if response.text else 'None'}")
            
            if not response.text or response.text.strip() == "":
                print("Empty response from Gemini API for plan generation")
                return {
                    "description": f"Plan for: {goal}",
                    "total_duration": f"{extracted_info.get('duration', 1)} days",
                    "days": []
                }
            
            # Clean the response text - remove markdown code blocks if present
            clean_text = response.text.strip()
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]  # Remove ```json
            if clean_text.startswith('```'):
                clean_text = clean_text[3:]   # Remove ```
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]  # Remove ending ```
            clean_text = clean_text.strip()
            
            print(f"Cleaned plan text: '{clean_text[:100]}...'")
            plan_data = json.loads(clean_text)
            return plan_data
        except Exception as e:
            print(f"Error generating plan: {e}")
            print(f"Plan response was: {getattr(response, 'text', 'No response object')}")
            # Return a basic plan structure
            return {
                "description": f"Plan for: {goal}",
                "total_duration": f"{extracted_info.get('duration', 1)} days",
                "days": []
            }
    
    async def _enrich_plan_with_external_data(self, plan_data: Dict[str, Any], external_info: Dict[str, Any], goal: str) -> Plan:
        """Enrich the plan with external information"""
        
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
                weather_info=external_info.get("weather", {}).get("forecast", {}).get("list", [])[:8] if external_info.get("weather") else None
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
