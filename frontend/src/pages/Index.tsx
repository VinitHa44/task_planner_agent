import { useState, useEffect } from "react";
import { Navigation } from "@/components/Navigation";
import { GoalInput } from "@/components/GoalInput";
import { PlanDisplay } from "@/components/PlanDisplay";
import { PlanHistory } from "@/components/PlanHistory";
import { LoadingState } from "@/components/LoadingState";
import { useToast } from "@/hooks/use-toast";
import { apiService } from "@/services/api";
import { transformPlanToDisplay, transformPlanToSummary } from "@/utils/dataTransform";
import { DisplayPlan, PlanSummary, PlanResponse } from "@/types/api";

// Types

const Index = () => {
  const [currentView, setCurrentView] = useState<'home' | 'plan' | 'history'>('home');
  const [currentPlan, setCurrentPlan] = useState<DisplayPlan | null>(null);
  const [planHistory, setPlanHistory] = useState<PlanSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState<'analyzing' | 'planning' | 'enriching' | 'finalizing'>('analyzing');
  const { toast } = useToast();

  // Load plan history on component mount
  useEffect(() => {
    loadPlanHistory();
  }, []);

  const loadPlanHistory = async () => {
    try {
      const plans = await apiService.getAllPlans();
      const summaries = plans.map(transformPlanToSummary);
      setPlanHistory(summaries);
    } catch (error) {
      console.error('Failed to load plan history:', error);
      toast({
        title: "Error",
        description: "Failed to load plan history",
        variant: "destructive"
      });
    }
  };

  const handleGoalSubmit = async (goal: string) => {
    setLoading(true);
    setCurrentView('plan');
    
    try {
      // Simulate AI processing stages for better UX
      setLoadingStage('analyzing');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setLoadingStage('planning');
      
      // Make actual API call to create plan
      const planResponse = await apiService.createPlan({ goal });
      
      setLoadingStage('enriching');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setLoadingStage('finalizing');
      await new Promise(resolve => setTimeout(resolve, 500));

      // Transform backend response to display format
      const displayPlan = transformPlanToDisplay(planResponse);
      setCurrentPlan(displayPlan);
      
      // Refresh plan history
      await loadPlanHistory();
      
      toast({
        title: "Plan Generated Successfully!",
        description: "Your personalized plan is ready. Start exploring your itinerary!"
      });
    } catch (error) {
      console.error('Failed to generate plan:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate plan. Please try again.",
        variant: "destructive"
      });
      setCurrentView('home');
    } finally {
      setLoading(false);
    }
  };

  const handleViewPlan = async (planId: string) => {
    try {
      const planResponse = await apiService.getPlan(planId);
      const displayPlan = transformPlanToDisplay(planResponse);
      setCurrentPlan(displayPlan);
      setCurrentView('plan');
    } catch (error) {
      console.error('Failed to load plan:', error);
      toast({
        title: "Error",
        description: "Failed to load plan",
        variant: "destructive"
      });
    }
  };

  const handleNavigation = (view: 'home' | 'plan' | 'history') => {
    setCurrentView(view);
    if (view === 'home') {
      setCurrentPlan(null);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation 
        currentView={currentView}
        onNavigate={handleNavigation}
        planCount={planHistory.length}
      />
      
      {currentView === 'home' && (
        <GoalInput onSubmit={handleGoalSubmit} loading={loading} />
      )}
      
      {currentView === 'plan' && (
        <>
          {loading ? (
            <LoadingState stage={loadingStage} />
          ) : currentPlan ? (
            <PlanDisplay plan={currentPlan} />
          ) : (
            <GoalInput onSubmit={handleGoalSubmit} loading={loading} />
          )}
        </>
      )}
      
      {currentView === 'history' && (
        <PlanHistory 
          plans={planHistory}
          onViewPlan={handleViewPlan}
        />
      )}
    </div>
  );
};

export default Index;
