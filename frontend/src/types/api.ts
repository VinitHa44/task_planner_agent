// Backend API Types - These match the Python Pydantic models

export interface Task {
  id?: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
  estimated_duration?: string;
  external_info?: Record<string, any>;
  created_at?: string;
}

export interface Day {
  day_number: number;
  date?: string;
  tasks: Task[];
  summary: string;
  weather_info?: Array<Record<string, any>>;
}

export interface Plan {
  id?: string;
  goal: string;
  description: string;
  days: Day[];
  total_duration: string;
  created_at?: string;
  updated_at?: string;
  status?: string;
}

export interface PlanCreate {
  goal: string;
  description?: string;
}

export interface PlanResponse extends Plan {
  id: string;
  created_at: string;
}

// Frontend-specific display types
export interface DisplayTask extends Task {
  duration: string;  // Required for PlanDisplay component (mapped from estimated_duration)
  time?: string;
  location?: string;
  completed?: boolean;
}

export interface WeatherInfo {
  condition: string;
  temperature: number;
  icon: string;
}

export interface DisplayDay {
  date: string;
  dayOfWeek: string;
  tasks: DisplayTask[];
  weather?: WeatherInfo;
}

export interface DisplayPlan {
  id: string;
  title: string;
  description: string;
  days: DisplayDay[];
  createdAt: string;
}

export interface PlanSummary {
  id: string;
  title: string;
  description: string;
  dayCount: number;
  createdAt: string;
  completedTasks?: number;
  totalTasks?: number;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface ApiError {
  detail: string;
}