import { PlanResponse, DisplayPlan, DisplayDay, DisplayTask, WeatherInfo, PlanSummary } from '@/types/api';
import { format, addDays } from 'date-fns';

// Transform backend weather data to display format
function transformWeatherInfo(weatherData?: Array<Record<string, any>>): WeatherInfo | undefined {
  console.log('🔄 Frontend dataTransform: transformWeatherInfo called');
  console.log('📥 Frontend dataTransform: Weather data:', JSON.stringify(weatherData, null, 2));

  if (!weatherData || weatherData.length === 0) {
    console.log('❌ Frontend dataTransform: No weather data available');
    return undefined;
  }
  
  const firstWeatherItem = weatherData[0];
  console.log('📥 Frontend dataTransform: First weather item:', JSON.stringify(firstWeatherItem, null, 2));
  
  // The backend weather data has this structure:
  // { date, day_name, min_temp, max_temp, avg_temp, condition, description, rain_probability, weather_advisory, etc. }
  const condition = firstWeatherItem.condition?.toLowerCase() || 'clear';
  const temperature = Math.round(firstWeatherItem.avg_temp || firstWeatherItem.max_temp || 25);
  
  console.log('📥 Frontend dataTransform: Extracted condition:', condition, 'temperature:', temperature);
  
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
  
  const transformed = {
    condition,
    temperature,
    icon: iconMap[condition] || 'sun',
    // Add additional weather details for display
    rainProbability: firstWeatherItem.rain_probability,
    minTemp: firstWeatherItem.min_temp,
    maxTemp: firstWeatherItem.max_temp,
    humidity: firstWeatherItem.humidity,
    windSpeed: firstWeatherItem.wind_speed,
    description: firstWeatherItem.description,
    weatherAdvisory: firstWeatherItem.weather_advisory,
    dataSource: firstWeatherItem.data_source,
  };

  console.log('📤 Frontend dataTransform: Transformed weather info:', JSON.stringify(transformed, null, 2));
  return transformed;
}

// Transform backend task to display task
function transformTask(task: any, index: number): DisplayTask {
  console.log(`🔄 Frontend dataTransform: transformTask called for task ${index}`);
  console.log('📥 Frontend dataTransform: Task data:', JSON.stringify(task, null, 2));

  const transformed = {
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

  console.log(`📤 Frontend dataTransform: Transformed task ${index}:`, JSON.stringify(transformed, null, 2));
  return transformed;
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

// Separate weather-related tasks from regular tasks
function separateWeatherTasks(tasks: any[]): { weatherTasks: any[], regularTasks: any[] } {
  const weatherTasks: any[] = [];
  const regularTasks: any[] = [];
  
  tasks.forEach(task => {
    const title = task.title?.toLowerCase() || '';
    const description = task.description?.toLowerCase() || '';
    
    // Check if task is weather-related
    const isWeatherTask = 
      title.includes('weather') ||
      description.includes('weather:') ||
      description.includes('🌤️') ||
      description.includes('☀️') ||
      description.includes('🌧️') ||
      description.includes('⛅') ||
      description.includes('°c') ||
      description.includes('activity impact:') ||
      description.includes('weather rating:') ||
      (task.estimated_duration === '0 hours' && description.includes('clouds'));
    
    if (isWeatherTask) {
      weatherTasks.push(task);
    } else {
      regularTasks.push(task);
    }
  });
  
  return { weatherTasks, regularTasks };
}

// Extract weather information from weather tasks
function extractWeatherFromTasks(weatherTasks: any[]): WeatherInfo | undefined {
  if (!weatherTasks || weatherTasks.length === 0) return undefined;
  
  const weatherTask = weatherTasks[0]; // Use first weather task
  const description = weatherTask.description || '';
  
  // Parse weather description like "🌤️ WEATHER: Light Rain, 25.1°C - 28.9°C, 100% - Activity Impact: Indoor science center and market visit."
  let condition = 'clear';
  let temperature = 25;
  let rainProbability: number | undefined;
  let minTemp: number | undefined;
  let maxTemp: number | undefined;
  let weatherAdvisory: string | undefined;
  
  // Extract condition
  if (description.includes('Rain') || description.includes('rain')) {
    condition = 'rain';
  } else if (description.includes('Clouds') || description.includes('clouds')) {
    condition = 'clouds';
  } else if (description.includes('Clear') || description.includes('clear')) {
    condition = 'clear';
  } else if (description.includes('Sunny') || description.includes('sunny')) {
    condition = 'clear';
  }
  
  // Extract temperature range (look for pattern like "25.1°C - 28.9°C")
  const tempRangeMatch = description.match(/(\d{1,2}\.?\d?)°C\s*-\s*(\d{1,2}\.?\d?)°C/);
  if (tempRangeMatch) {
    minTemp = parseFloat(tempRangeMatch[1]);
    maxTemp = parseFloat(tempRangeMatch[2]);
    temperature = Math.round((minTemp + maxTemp) / 2); // Use average
  } else {
    // Single temperature pattern
    const tempMatch = description.match(/(\d{1,2}\.?\d?)°C/);
    if (tempMatch) {
      temperature = Math.round(parseFloat(tempMatch[1]));
    }
  }
  
  // Extract rain probability (look for pattern like "100%")
  const rainMatch = description.match(/(\d{1,3})%/);
  if (rainMatch) {
    rainProbability = parseInt(rainMatch[1]);
  }
  
  // Extract weather advisory (text after "Activity Impact:")
  const advisoryMatch = description.match(/Activity Impact:\s*([^.]+)/);
  if (advisoryMatch) {
    weatherAdvisory = advisoryMatch[1].trim();
  }
  
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
    rainProbability,
    minTemp,
    maxTemp,
    weatherAdvisory,
    dataSource: 'extracted from tasks',
  };
}

// Transform backend day to display day
function transformDay(day: any, dayIndex: number, baseDate: Date, actualDate?: string): DisplayDay {
  console.log(`🔄 Frontend dataTransform: transformDay called for day ${dayIndex}`);
  console.log('📥 Frontend dataTransform: Day data:', JSON.stringify(day, null, 2));
  console.log('📥 Frontend dataTransform: Base date:', baseDate);
  console.log('📥 Frontend dataTransform: Actual date from backend:', actualDate);

  // Use the actual date from backend if available, otherwise calculate from base date
  const dayDate = actualDate ? new Date(actualDate) : addDays(baseDate, dayIndex);
  console.log('📥 Frontend dataTransform: Final day date:', dayDate);
  
  // Separate weather-related tasks from regular tasks
  const { weatherTasks, regularTasks } = separateWeatherTasks(day.tasks || []);
  console.log('📥 Frontend dataTransform: Weather tasks found:', weatherTasks.length);
  console.log('📥 Frontend dataTransform: Regular tasks:', regularTasks.length);
  
  // Use weather_info if available, otherwise try to extract from weather tasks
  let weatherInfo = transformWeatherInfo(day.weather_info);
  if (!weatherInfo && weatherTasks.length > 0) {
    weatherInfo = extractWeatherFromTasks(weatherTasks);
  }
  
  const transformed = {
    date: day.date || format(dayDate, 'yyyy-MM-dd'),
    dayOfWeek: format(dayDate, 'EEEE'),
    tasks: regularTasks.map((task: any, taskIndex: number) => {
      console.log(`🔄 Frontend dataTransform: Transforming task ${taskIndex}:`, JSON.stringify(task, null, 2));
      return transformTask(task, taskIndex);
    }),
    weather: weatherInfo,
  };

  console.log(`📤 Frontend dataTransform: Transformed day ${dayIndex}:`, JSON.stringify(transformed, null, 2));
  return transformed;
}

// Transform backend plan to display plan
export function transformPlanToDisplay(plan: PlanResponse): DisplayPlan {
  console.log('🔄 Frontend dataTransform: transformPlanToDisplay called');
  console.log('📥 Frontend dataTransform: Input plan response:', JSON.stringify(plan, null, 2));

  // Use the actual date from the first day if available, otherwise fall back to created_at
  const firstDayDate = plan.days.length > 0 && plan.days[0].date ? new Date(plan.days[0].date) : null;
  const baseDate = firstDayDate || (plan.created_at ? new Date(plan.created_at) : new Date());
  console.log('📥 Frontend dataTransform: First day date:', firstDayDate);
  console.log('📥 Frontend dataTransform: Base date calculated:', baseDate);
  
  const transformed = {
    id: plan.id,
    title: plan.goal, // Use goal as title
    description: plan.description,
    days: plan.days.map((day, index) => {
      console.log(`🔄 Frontend dataTransform: Transforming day ${index}:`, JSON.stringify(day, null, 2));
      // Use the actual date from backend instead of calculating from base date
      return transformDay(day, index, baseDate, day.date);
    }),
    createdAt: plan.created_at || new Date().toISOString(),
  };

  console.log('📤 Frontend dataTransform: Transformed result:', JSON.stringify(transformed, null, 2));
  return transformed;
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