import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { 
  Calendar, 
  Clock, 
  Search, 
  Eye,
  Trash2,
  MapPin
} from "lucide-react";
import { useState } from "react";

interface PlanSummary {
  id: string;
  title: string;
  description: string;
  dayCount: number;
  createdAt: string;
  completedTasks?: number;
  totalTasks?: number;
}

interface PlanHistoryProps {
  plans: PlanSummary[];
  onViewPlan: (planId: string) => void;
  onDeletePlan?: (planId: string) => void;
}

export const PlanHistory = ({ plans, onViewPlan, onDeletePlan }: PlanHistoryProps) => {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredPlans = plans.filter(plan =>
    plan.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    plan.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (plans.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center">
          <div className="bg-muted rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-6">
            <Calendar className="w-8 h-8 text-muted-foreground" />
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-4">
            No Plans Yet
          </h2>
          <p className="text-muted-foreground mb-8">
            Start by creating your first AI-powered plan! Describe any goal and watch it transform into a detailed roadmap.
          </p>
          <Button variant="hero" size="lg" onClick={() => window.location.reload()}>
            Create Your First Plan
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-4">
          Your Plans
        </h1>
        <p className="text-muted-foreground mb-6">
          All your AI-generated plans in one place. Click to view details or create a new one.
        </p>
        
        {/* Search */}
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search your plans..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Plans Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {filteredPlans.map((plan) => (
          <Card key={plan.id} className="plan-card p-6 cursor-pointer" onClick={() => onViewPlan(plan.id)}>
            <div className="space-y-4">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-foreground truncate mb-2">
                    {plan.title}
                  </h3>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {plan.description}
                  </p>
                </div>
                
                {onDeletePlan && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="ml-2 text-muted-foreground hover:text-destructive"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeletePlan(plan.id);
                    }}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>

              {/* Stats */}
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {plan.dayCount} days
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {formatDate(plan.createdAt)}
                </div>
                {plan.totalTasks && (
                  <div className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    {plan.completedTasks || 0}/{plan.totalTasks} tasks
                  </div>
                )}
              </div>

              {/* Progress */}
              {plan.totalTasks && plan.totalTasks > 0 && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="text-muted-foreground">
                      {Math.round(((plan.completedTasks || 0) / plan.totalTasks) * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-primary to-secondary h-2 rounded-full transition-all duration-300"
                      style={{ width: `${Math.round(((plan.completedTasks || 0) / plan.totalTasks) * 100)}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Action */}
              <div className="pt-2">
                <Button variant="outline" size="sm" className="w-full">
                  <Eye className="w-4 h-4 mr-2" />
                  View Plan
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {filteredPlans.length === 0 && searchTerm && (
        <div className="text-center py-12">
          <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-foreground mb-2">
            No plans found
          </h3>
          <p className="text-muted-foreground">
            Try adjusting your search terms or create a new plan.
          </p>
        </div>
      )}
    </div>
  );
};