import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Sparkles, Brain, Calendar, MapPin } from "lucide-react";

interface LoadingStateProps {
  stage?: 'analyzing' | 'planning' | 'enriching' | 'finalizing';
}

const stages = {
  analyzing: {
    icon: Brain,
    title: "Analyzing your goal",
    description: "Understanding what you want to achieve..."
  },
  planning: {
    icon: Calendar,
    title: "Creating your plan",
    description: "Breaking down into day-by-day activities..."
  },
  enriching: {
    icon: MapPin,
    title: "Adding details",
    description: "Fetching weather data and location info..."
  },
  finalizing: {
    icon: Sparkles,
    title: "Finalizing your plan",
    description: "Putting the finishing touches..."
  }
};

export const LoadingState = ({ stage = 'analyzing' }: LoadingStateProps) => {
  const currentStage = stages[stage];
  const Icon = currentStage.icon;

  return (
    <div className="max-w-4xl mx-auto px-4 py-16">
      {/* Loading Header */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center mb-6">
          <div className="bg-gradient-to-br from-primary to-secondary rounded-full p-4 animate-glow">
            <Icon className="w-8 h-8 text-white animate-pulse" />
          </div>
        </div>
        <h2 className="text-3xl font-bold text-foreground mb-4">
          {currentStage.title}
        </h2>
        <p className="text-lg text-muted-foreground">
          {currentStage.description}
        </p>
      </div>

      {/* Loading Progress */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          {Object.entries(stages).map(([key, { icon: StageIcon, title }], index) => {
            const isActive = key === stage;
            const isCompleted = Object.keys(stages).indexOf(key) < Object.keys(stages).indexOf(stage);
            
            return (
              <div key={key} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full transition-all ${
                  isActive ? 'bg-primary text-primary-foreground scale-110' :
                  isCompleted ? 'bg-success text-success-foreground' :
                  'bg-muted text-muted-foreground'
                }`}>
                  <StageIcon className="w-5 h-5" />
                </div>
                {index < Object.keys(stages).length - 1 && (
                  <div className={`w-16 h-1 mx-2 rounded-full ${
                    isCompleted ? 'bg-success' : 'bg-muted'
                  }`} />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Loading Cards */}
      <div className="space-y-6">
        {[1, 2, 3].map((day) => (
          <Card key={day} className="plan-card p-6">
            <div className="flex items-center gap-4 mb-6">
              <Skeleton className="w-16 h-16 rounded-full" />
              <div className="flex-1">
                <Skeleton className="h-6 w-32 mb-2" />
                <Skeleton className="h-4 w-48" />
              </div>
              <Skeleton className="h-8 w-24 rounded-full" />
            </div>
            
            <div className="space-y-4">
              {[1, 2, 3, 4].map((task) => (
                <div key={task} className="task-card rounded-xl p-4">
                  <div className="flex items-start gap-4">
                    <Skeleton className="w-5 h-5 rounded-full mt-1" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <Skeleton className="h-5 w-48" />
                        <div className="flex gap-2">
                          <Skeleton className="h-6 w-16 rounded-full" />
                          <Skeleton className="h-6 w-20 rounded-full" />
                        </div>
                      </div>
                      <Skeleton className="h-4 w-full mb-2" />
                      <Skeleton className="h-4 w-3/4 mb-2" />
                      <Skeleton className="h-3 w-32" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};