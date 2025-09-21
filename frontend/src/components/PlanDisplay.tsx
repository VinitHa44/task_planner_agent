import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Calendar, 
  Clock, 
  MapPin,
  Cloud,
  Sun,
  CloudRain,
  Snowflake
} from "lucide-react";
import { useState } from "react";
import { DisplayPlan, DisplayTask, DisplayDay } from "@/types/api";

interface PlanDisplayProps {
  plan: DisplayPlan;
}

const WeatherIcon = ({ condition }: { condition: string }) => {
  const iconClass = "w-5 h-5";
  
  switch (condition.toLowerCase()) {
    case 'sunny':
    case 'clear':
      return <Sun className={`${iconClass} text-yellow-500`} />;
    case 'cloudy':
    case 'overcast':
      return <Cloud className={`${iconClass} text-gray-500`} />;
    case 'rainy':
    case 'rain':
      return <CloudRain className={`${iconClass} text-blue-500`} />;
    case 'snowy':
    case 'snow':
      return <Snowflake className={`${iconClass} text-gray-300`} />;
    default:
      return <Sun className={`${iconClass} text-yellow-500`} />;
  }
};

export const PlanDisplay = ({ plan }: PlanDisplayProps) => {
  const [expandedDays, setExpandedDays] = useState<Set<number>>(new Set([0]));

  const toggleDay = (dayIndex: number) => {
    const newExpanded = new Set(expandedDays);
    if (newExpanded.has(dayIndex)) {
      newExpanded.delete(dayIndex);
    } else {
      newExpanded.add(dayIndex);
    }
    setExpandedDays(newExpanded);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Plan Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-foreground mb-4">
          {plan.title}
        </h1>
        <p className="text-xl text-muted-foreground mb-6">
          {plan.description}
        </p>
        <div className="flex items-center justify-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            {plan.days.length} days
          </div>
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            Created {new Date(plan.createdAt).toLocaleDateString()}
          </div>
        </div>
      </div>

      {/* Days */}
      <div className="space-y-6">
        {plan.days.map((day, dayIndex) => (
          <Card key={dayIndex} className="plan-card overflow-hidden">
            {/* Day Header */}
            <div 
              className="p-6 cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => toggleDay(dayIndex)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-2xl font-bold text-primary">
                    Day {dayIndex + 1}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-foreground">
                      {day.dayOfWeek}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {(() => {
                        try {
                          const date = new Date(day.date);
                          if (isNaN(date.getTime())) {
                            return day.date; // Fallback to raw date string
                          }
                          return date.toLocaleDateString('en-US', {
                            month: 'long',
                            day: 'numeric',
                            year: 'numeric'
                          });
                        } catch (error) {
                          return day.date; // Fallback to raw date string
                        }
                      })()}
                    </p>
                  </div>
                </div>
                
                {day.weather && (
                  <div className="bg-muted rounded-lg px-3 py-2 space-y-1">
                    <div className="flex items-center gap-2">
                      <WeatherIcon condition={day.weather.condition} />
                      <span className="text-sm font-medium">
                        {day.weather.temperature}°C
                      </span>
                      <span className="text-xs text-muted-foreground capitalize">
                        {day.weather.condition}
                      </span>
                    </div>
                    
                    {/* Temperature range */}
                    {day.weather.minTemp && day.weather.maxTemp && (
                      <div className="text-xs text-muted-foreground">
                        Range: {Math.round(day.weather.minTemp)}°C - {Math.round(day.weather.maxTemp)}°C
                      </div>
                    )}
                    
                    {/* Rain probability */}
                    {day.weather.rainProbability !== undefined && (
                      <div className="text-xs text-muted-foreground">
                        🌧️ Rain: {day.weather.rainProbability}%
                      </div>
                    )}
                    
                    {/* Weather advisory */}
                    {day.weather.weatherAdvisory && (
                      <div className="text-xs text-orange-600 font-medium">
                        ⚠️ {day.weather.weatherAdvisory}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Tasks */}
            {expandedDays.has(dayIndex) && (
              <div className="px-6 pb-6">
                <div className="space-y-4">
                  {day.tasks.map((task, taskIndex) => (
                    <div key={task.id} className="task-card rounded-xl p-4">
                      <div className="flex items-start gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-4 mb-2">
                            <h4 className="font-semibold text-foreground">
                              {task.title}
                            </h4>
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              {task.time && (
                                <Badge variant="outline" className="text-xs">
                                  <Clock className="w-3 h-3 mr-1" />
                                  {task.time}
                                </Badge>
                              )}
                              <Badge variant="outline" className="text-xs">
                                {task.duration}
                              </Badge>
                            </div>
                          </div>
                          
                          <p className="text-sm mb-2 text-muted-foreground">
                            {task.description}
                          </p>
                          
                          {task.location && (
                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                              <MapPin className="w-3 h-3" />
                              {task.location}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
};