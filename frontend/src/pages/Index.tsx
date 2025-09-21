import { useState, useEffect } from "react";
import { Navigation } from "@/components/Navigation";
import { GoalInput } from "@/components/GoalInput";
import { PlanDisplay } from "@/components/PlanDisplay";
import { PlanHistory } from "@/components/PlanHistory";
import { LoadingState } from "@/components/LoadingState";
import { ErrorNotification } from "@/components/ErrorNotification";
import { useToast } from "@/hooks/use-toast";
import { apiService } from "@/services/api";
import { transformPlanToDisplay, transformPlanToSummary } from "@/utils/dataTransform";
import { DisplayPlan, PlanSummary, PlanResponse } from "@/types/api";
import { ErrorHandler } from "@/services/errorHandler";

// Types

const Index = () => {
  const [currentView, setCurrentView] = useState<'home' | 'plan' | 'history'>('home');
  const [currentPlan, setCurrentPlan] = useState<DisplayPlan | null>(null);
  const [planHistory, setPlanHistory] = useState<PlanSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState<'analyzing' | 'planning' | 'enriching' | 'finalizing'>('analyzing');
  const [error, setError] = useState<any>(null);
  const [lastFailedGoal, setLastFailedGoal] = useState<string>('');
  const { toast } = useToast();

  // Load plan history on component mount
  useEffect(() => {
    loadPlanHistory();
  }, []);

  const clearError = () => {
    setError(null);
  };

  const handleError = (error: any, context?: string) => {
    console.log(`❌ Frontend Index: Error in ${context || 'unknown context'}`);
    console.log('📥 Frontend Index: Error object:', error);
    console.log('📥 Frontend Index: Error type:', typeof error);
    console.log('📥 Frontend Index: Error keys:', Object.keys(error || {}));
    
    setError(error);
    
    // Also show a toast for immediate feedback
    const errorInfo = ErrorHandler.getErrorMessage(error);
    console.log('📤 Frontend Index: Processed error info:', errorInfo);
    
    toast({
      title: "Error",
      description: errorInfo.message,
      variant: "destructive"
    });
  };

  const loadPlanHistory = async () => {
    try {
      const plans = await apiService.getAllPlans();
      const summaries = plans.map(transformPlanToSummary);
      setPlanHistory(summaries);
      clearError(); // Clear any previous errors on successful load
    } catch (error) {
      handleError(error, 'loadPlanHistory');
    }
  };

  const handleGoalSubmit = async (goal: string) => {
    console.log('🔄 Frontend Index: handleGoalSubmit called');
    console.log('📥 Frontend Index: Goal:', goal);
    
    setLoading(true);
    setCurrentView('plan');
    setLastFailedGoal(goal);
    clearError(); // Clear any previous errors
    
    try {
      // Simulate AI processing stages for better UX
      console.log('🔄 Frontend Index: Starting processing stages');
      setLoadingStage('analyzing');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setLoadingStage('planning');
      
      console.log('🔄 Frontend Index: Calling API to create plan');
      // Make actual API call to create plan
      const planResponse = await apiService.createPlan({ goal });
      console.log('✅ Frontend Index: API call successful');
      console.log('📤 Frontend Index: Plan response:', planResponse);
      
      setLoadingStage('enriching');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setLoadingStage('finalizing');
      await new Promise(resolve => setTimeout(resolve, 500));

      console.log('🔄 Frontend Index: Transforming plan to display format');
      // Transform backend response to display format
      const displayPlan = transformPlanToDisplay(planResponse);
      console.log('📤 Frontend Index: Display plan:', displayPlan);
      setCurrentPlan(displayPlan);
      
      // Refresh plan history
      console.log('🔄 Frontend Index: Refreshing plan history');
      await loadPlanHistory();
      
      console.log('✅ Frontend Index: Plan creation completed successfully');
      toast({
        title: "Plan Generated Successfully!",
        description: "Your personalized plan is ready. Start exploring your itinerary!"
      });
    } catch (error) {
      console.log('❌ Frontend Index: Plan creation failed');
      handleError(error, 'handleGoalSubmit');
      setCurrentView('home');
    } finally {
      setLoading(false);
      console.log('🔄 Frontend Index: Loading state cleared');
    }
  };

  const handleRetry = () => {
    if (lastFailedGoal) {
      clearError();
      handleGoalSubmit(lastFailedGoal);
    } else {
      // If no specific failed goal, try to reload plans
      clearError();
      loadPlanHistory();
    }
  };

  const handleViewPlan = async (planId: string) => {
    try {
      clearError();
      const planResponse = await apiService.getPlan(planId);
      const displayPlan = transformPlanToDisplay(planResponse);
      setCurrentPlan(displayPlan);
      setCurrentView('plan');
    } catch (error) {
      handleError(error, 'handleViewPlan');
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
      
      {/* Error Notification */}
      {error && (
        <div className="container mx-auto px-4 pt-4">
          <ErrorNotification
            error={error}
            onRetry={handleRetry}
            onDismiss={clearError}
          />
        </div>
      )}
      
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
