"""
AI service for integrating with generative AI models (Gemini)
"""
import google.generativeai as genai
import os
import json
from typing import Dict, Any
from datetime import datetime
import logging
from utils.trip_logger import TripLogger

class AIService:
    """Service for AI/LLM integration"""
    
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.logger = logging.getLogger(__name__)
    
    async def extract_goal_information(self, goal: str, logger: TripLogger = None) -> Dict[str, Any]:
        """Extract key information from a user's goal using AI"""
        if logger:
            logger.log_step("🧠 AI: Analyzing goal for key information", {
                "goal": goal
            })
        
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
        - timing_keywords (extract any timing references like "next week", "tomorrow", "this weekend", "in 3 days")
        
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
        
        try:
            response = self.model.generate_content(prompt)
            
            if not response.text or response.text.strip() == "":
                if logger:
                    logger.log_error("Empty response from Gemini API", {})
                return self._get_default_goal_info()
            
            # Clean the response text - remove markdown code blocks if present
            clean_text = self._clean_json_response(response.text)
            extracted = json.loads(clean_text)
            
            # Process and validate the extracted information
            result = self._process_extracted_info(extracted)
            
            if logger:
                logger.log_success("Goal information extracted successfully", {
                    "extracted_info": result
                })
            
            return result
            
        except Exception as e:
            if logger:
                logger.log_error(f"Error extracting goal info: {e}", {
                    "exception_type": type(e).__name__,
                    "exception_message": str(e)
                })
            return self._get_default_goal_info()
    
    async def generate_plan_structure(self, goal: str, description: str, extracted_info: Dict[str, Any], 
                                    external_info: Dict[str, Any], today: datetime, logger: TripLogger = None) -> Dict[str, Any]:
        """Generate the main plan structure using AI"""
        
        if logger:
            logger.log_step("🔄 AIService: Starting plan structure generation", {
                "goal": goal,
                "description": description,
                "extracted_info": extracted_info,
                "has_external_info": bool(external_info),
                "today": today.isoformat()
            })
        
        # Prepare context for the LLM
        context = self._prepare_plan_context(goal, description, extracted_info, external_info, today)
        
        prompt = f"""
        {context}
        
        Create a detailed day-by-day travel plan for this goal. 
        
        IMPORTANT: Use the exact trip dates provided above. Each day in your plan should correspond to the specific dates and weather forecasts provided.
        
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
        
        2. **WEATHER-SMART PLANNING (MANDATORY):**
           - ANALYZE each day's weather forecast provided above
           - If rainy/stormy weather predicted: prioritize INDOOR activities (museums, shopping malls, covered markets, restaurants)
           - If very hot (>40°C): plan early morning (6-10 AM) and evening (5-8 PM) outdoor activities, midday (11 AM-4 PM) MUST be indoor
           - If very cold or extreme weather: add weather warnings and suggest alternative indoor options
           - For each activity, EXPLICITLY mention how weather affects the choice: "Due to 80% rain probability, visiting the indoor City Palace instead of outdoor Amber Fort"
           - Rate weather suitability for each day: "Weather Rating: X/10 for outdoor activities"
           - Include weather-appropriate clothing suggestions
        
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
        
        6. **WEATHER ADVISORY SYSTEM (ENHANCED):**
           - Start each day with: "🌤️ WEATHER: [condition], [temp range], [rain probability]% - Activity Impact: [how it affects plan]"
           - If extreme weather (storm, extreme heat/cold): "⚠️ WEATHER ADVISORY: [condition] - Plan modified for indoor activities"
           - Rate each day's weather suitability (1-10 scale) for outdoor activities
           - Suggest weather-appropriate backup plans for outdoor activities
        
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
        
        Requirements:
        - Create exactly {extracted_info.get('duration', 1)} days
        - Use the EXACT dates provided in the trip dates section above
        - For each day, reference the weather forecast and adapt activities accordingly
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
        - MANDATORY: Every activity choice must consider the weather forecast for that specific day
        - Account for weather conditions and suggest alternatives
        - Prioritize arrival logistics and smart hotel location
        - Focus on quality experiences over quantity of places
        - LET THE TIME MATH DETERMINE NUMBER OF ACTIVITIES, NOT PRE-SET LIMITS
        
        Return only valid JSON.
        """
        
        try:
            if logger:
                logger.log_step("🔄 AIService: Calling Gemini API", {
                    "model": self.model.model_name if hasattr(self.model, 'model_name') else "Unknown",
                    "prompt_length": len(prompt)
                })
            
            response = self.model.generate_content(prompt)
            
            if logger:
                logger.log_step("🔄 AIService: Gemini API response received", {
                    "response_type": type(response).__name__,
                    "has_text": hasattr(response, 'text') and response.text is not None,
                    "text_length": len(response.text) if hasattr(response, 'text') and response.text else 0
                })
            
            if not response.text or response.text.strip() == "":
                if logger:
                    logger.log_error("Empty response from Gemini API for plan generation", {})
                return self._get_default_plan_structure(goal, extracted_info)
            
            # Clean the response text - remove markdown code blocks if present
            clean_text = self._clean_json_response(response.text)
            plan_data = json.loads(clean_text)
            
            if logger:
                logger.log_success("Plan structure generated successfully", {
                    "plan_type": type(plan_data).__name__,
                    "has_days": "days" in plan_data,
                    "num_days": len(plan_data.get("days", [])),
                    "description": plan_data.get("description", "")
                })
            
            return plan_data
            
        except Exception as e:
            if logger:
                logger.log_error("Exception in generate_plan_structure", {
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                    "exception_args": str(e.args)
                })
            
            return self._get_default_plan_structure(goal, extracted_info)
    
    def _clean_json_response(self, response_text: str) -> str:
        """Clean JSON response from AI model"""
        clean_text = response_text.strip()
        if clean_text.startswith('```json'):
            clean_text = clean_text[7:]  # Remove ```json
        if clean_text.startswith('```'):
            clean_text = clean_text[3:]   # Remove ```
        if clean_text.endswith('```'):
            clean_text = clean_text[:-3]  # Remove ending ```
        return clean_text.strip()
    
    def _process_extracted_info(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate extracted information"""
        # Parse duration safely - handle both numbers and strings like "7+"
        duration_value = extracted.get("duration", 3)
        if isinstance(duration_value, str):
            # Handle strings like "7+", "5-7", etc.
            import re
            numbers = re.findall(r'\d+', str(duration_value))
            if numbers:
                duration_value = int(numbers[0])
            else:
                duration_value = 3  # Default fallback
        elif not isinstance(duration_value, int):
            duration_value = 3  # Default for any other type
        
        # Ensure minimum 1 day
        duration_value = max(1, duration_value)
        
        # Clean up null values and ensure proper types
        return {
            "destination": extracted.get("destination") or "",
            "duration": duration_value,
            "activities": extracted.get("activities") or [],
            "preferences": extracted.get("preferences") or [],
            "budget_considerations": extracted.get("budget_considerations") or "",
            "time_of_year": extracted.get("time_of_year") or "",
            "timing_keywords": extracted.get("timing_keywords") or ""
        }
    
    def _prepare_plan_context(self, goal: str, description: str, extracted_info: Dict[str, Any], 
                            external_info: Dict[str, Any], today: datetime) -> str:
        """Prepare context for plan generation"""
        today_str = today.strftime("%A, %B %d, %Y")
        
        # Prepare weather context
        weather_context = "No weather data available"
        weather_source_info = ""
        
        if external_info.get("weather", {}).get("daily_forecasts"):
            weather_data = external_info["weather"]
            weather_source_info = f"\n🌐 Weather Data Source: {weather_data.get('weather_source', 'Unknown')}"
            if not weather_data.get("forecast_available", True):
                weather_source_info += f"\n📅 Days until trip: {weather_data.get('days_until_trip', 'Unknown')}"
                weather_source_info += "\nNote: Using seasonal estimates for distant trip dates"
            
            weather_context = "Daily Weather Information for Trip:" + weather_source_info + "\n\n"
            
            for day_weather in weather_data["daily_forecasts"]:
                weather_context += f"  📅 {day_weather['date']} ({day_weather['day_name']}):\n"
                
                # Show temperature range
                weather_context += f"    🌡️ Temperature: {day_weather['min_temp']}°C - {day_weather['max_temp']}°C"
                if 'avg_temp' in day_weather:
                    weather_context += f" (avg: {day_weather['avg_temp']}°C)"
                weather_context += "\n"
                
                # Show weather condition
                if 'condition' in day_weather and 'description' in day_weather:
                    weather_context += f"    🌤️ Condition: {day_weather['condition']} - {day_weather['description']}\n"
                
                # Show data source for this day
                data_source = day_weather.get('data_source', 'Unknown')
                if data_source == "Seasonal estimate (forecast unavailable)":
                    weather_context += f"    📊 Data: {data_source} ({day_weather.get('season', 'Unknown')} season)\n"
                else:
                    weather_context += f"    📊 Data: {data_source}\n"
                
                # Show rain information if available
                if 'rain_probability' in day_weather:
                    weather_context += f"    💧 Rain probability: {day_weather['rain_probability']}%\n"
                    if day_weather.get('total_rain_mm', 0) > 0:
                        weather_context += f"    🌧️ Expected rainfall: {day_weather['total_rain_mm']}mm\n"
                
                # Show additional weather details if available
                if 'humidity' in day_weather:
                    humidity_text = f"Humidity: {day_weather['humidity']}%"
                    if 'wind_speed' in day_weather:
                        humidity_text += f", Wind: {day_weather['wind_speed']} m/s"
                    weather_context += f"    💨 {humidity_text}\n"
                
                # Show weather advisory
                weather_context += f"    ⚠️ Activity Advisory: {day_weather['weather_advisory']}\n"
                weather_context += "\n"
        
        trip_dates_info = ""
        if external_info.get("trip_start_date") and external_info.get("trip_end_date"):
            start_date = external_info["trip_start_date"]
            end_date = external_info["trip_end_date"]
            trip_dates_info = f"""
        Trip Dates: {start_date.strftime('%A, %B %d, %Y')} to {end_date.strftime('%A, %B %d, %Y')}
        Duration: {external_info.get('trip_duration', 1)} days
        """
        
        return f"""
        Goal: {goal}
        Description: {description or "No additional description provided"}
        Today's Date: {today_str}
        {trip_dates_info}
        
        Extracted Information:
        - Destination: {extracted_info.get('destination', 'Not specified')}
        - Duration: {extracted_info.get('duration', 1)} days
        - Activities: {', '.join(str(x) for x in extracted_info.get('activities', []))}
        - Preferences: {', '.join(str(x) for x in extracted_info.get('preferences', []))}
        
        {weather_context}
        
        External Information Available:
        - Weather data: {'Yes' if external_info.get('weather') else 'No'}
        - Web search results: {len(external_info.get('search_results', {}))} queries
        """
    
    def _get_default_goal_info(self) -> Dict[str, Any]:
        """Get default goal information when extraction fails"""
        return {
            "destination": "",
            "duration": 3,
            "activities": [],
            "preferences": [],
            "budget_considerations": "",
            "time_of_year": "",
            "timing_keywords": ""
        }
    
    def _get_default_plan_structure(self, goal: str, extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get default plan structure when generation fails"""
        return {
            "description": f"Plan for: {goal}",
            "total_duration": f"{extracted_info.get('duration', 1)} days",
            "days": []
        }