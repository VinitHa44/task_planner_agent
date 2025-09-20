import { PlanResponse, DisplayPlan, DisplayDay, DisplayTask, WeatherInfo, PlanSummary } from '@/types/api';
import { format, addDays } from 'date-fns';

// Transform backend weather data to display format
function transformWeatherInfo(weatherData?: Array<Record<string, any>>): WeatherInfo | undefined {
  if (!weatherData || weatherData.length === 0) return undefined;
  
  const firstWeatherItem = weatherData[0];
  
  // Extract weather condition and temperature from OpenWeather API format
  const condition = firstWeatherItem.weather?.[0]?.main?.toLowerCase() || 'clear';
  const temperature = Math.round(firstWeatherItem.main?.temp || 25);
  
  // Map weather conditions to icons
  const iconMap: Record<string, string> = {
    'clear': 'sun',
    'clouds': 'cloud',
    'rain': 'cloud-rain',
    'drizzle': 'cloud-drizzle',
    'thunderstorm': 'cloud-lightning',
    'snow': 'cloud-snow',
    'mist': 'cloud',
    'fog': 'cloud',
    'haze': 'cloud',
  };
  
  return {
    condition,
    temperature,
    icon: iconMap[condition] || 'sun',
  };
}

// Transform backend task to display task
function transformTask(task: any, index: number): DisplayTask {
  return {
    id: task.id || `task-${index}`,
    title: task.title,
    description: task.description,
    status: task.status || 'pending',
    estimated_duration: task.estimated_duration,
    duration: task.estimated_duration || '1 hour', // Map estimated_duration to duration for PlanDisplay
    completed: task.status === 'completed',
    // Extract time and location from description if possible
    time: extractTimeFromDescription(task.description),
    location: extractLocationFromDescription(task.description),
  };
}

// Simple regex to extract time patterns from descriptions
function extractTimeFromDescription(description: string): string | undefined {
  const timeMatch = description.match(/(\d{1,2}:\d{2}\s*(AM|PM|am|pm))/i);
  return timeMatch ? timeMatch[0] : undefined;
}

// Simple extraction of location patterns
function extractLocationFromDescription(description: string): string | undefined {
  // Look for patterns like "at Location", "in Location", "Location area"
  const locationMatch = description.match(/(at|in|near)\s+([A-Z][a-zA-Z\s]+?)(?:[,.;]|$)/);
  return locationMatch ? locationMatch[2].trim() : undefined;
}

// Transform backend day to display day
function transformDay(day: any, dayIndex: number, baseDate: Date): DisplayDay {
  const dayDate = addDays(baseDate, dayIndex);
  
  return {
    date: day.date || format(dayDate, 'yyyy-MM-dd'),
    dayOfWeek: format(dayDate, 'EEEE'),
    tasks: day.tasks.map((task: any, taskIndex: number) => transformTask(task, taskIndex)),
    weather: transformWeatherInfo(day.weather_info),
  };
}

// Transform backend plan to display plan
export function transformPlanToDisplay(plan: PlanResponse): DisplayPlan {
  const baseDate = plan.created_at ? new Date(plan.created_at) : new Date();
  
  return {
    id: plan.id,
    title: plan.goal, // Use goal as title
    description: plan.description,
    days: plan.days.map((day, index) => transformDay(day, index, baseDate)),
    createdAt: plan.created_at || new Date().toISOString(),
  };
}

// Transform plan to summary
export function transformPlanToSummary(plan: PlanResponse): PlanSummary {
  const totalTasks = plan.days.reduce((sum, day) => sum + day.tasks.length, 0);
  const completedTasks = plan.days.reduce(
    (sum, day) => sum + day.tasks.filter(task => task.status === 'completed').length,
    0
  );
  
  return {
    id: plan.id,
    title: plan.goal,
    description: plan.description,
    dayCount: plan.days.length,
    createdAt: plan.created_at || new Date().toISOString(),
    totalTasks,
    completedTasks,
  };
}

// Extract goal title from a longer goal description
export function extractGoalTitle(goal: string): string {
  // Take first sentence or first 50 characters
  const firstSentence = goal.split('.')[0];
  return firstSentence.length > 50 ? firstSentence.substring(0, 50) + '...' : firstSentence;
}