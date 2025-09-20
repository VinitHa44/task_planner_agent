import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Sparkles, Send } from "lucide-react";
import heroBg from "@/assets/hero-bg.jpg";

interface GoalInputProps {
  onSubmit: (goal: string) => void;
  loading?: boolean;
}

export const GoalInput = ({ onSubmit, loading }: GoalInputProps) => {
  const [goal, setGoal] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (goal.trim() && !loading) {
      onSubmit(goal.trim());
    }
  };

  return (
    <div 
      className="relative min-h-[60vh] flex items-center justify-center px-4 py-16 overflow-hidden"
      style={{
        backgroundImage: `linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url(${heroBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed'
      }}
    >
      <div className="w-full max-w-4xl">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <div className="bg-white/10 backdrop-blur-sm rounded-full p-4 animate-float">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Plan Anything with AI
          </h1>
          <p className="text-xl md:text-2xl text-white/90 max-w-2xl mx-auto">
            Transform your ideas into detailed, actionable plans. From trips to projects, 
            let AI create your perfect day-by-day roadmap.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="hero-card rounded-2xl p-8 max-w-3xl mx-auto">
          <div className="space-y-6">
            <div>
              <label htmlFor="goal" className="block text-lg font-semibold text-card-foreground mb-3">
                What would you like to plan?
              </label>
              <Textarea
                id="goal"
                placeholder="Describe your goal... For example: 'Plan a 3-day cultural trip to Jaipur with amazing food and historical sites' or 'Create a 7-day workout routine for beginners'"
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                className="min-h-[120px] text-lg resize-none"
                disabled={loading}
              />
            </div>
            
            <Button 
              type="submit" 
              variant="hero"
              size="lg"
              disabled={!goal.trim() || loading}
              className="w-full"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="loading-pulse w-5 h-5 bg-current rounded-full" />
                  Generating Your Plan...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Send className="w-5 h-5" />
                  Generate My Plan
                </div>
              )}
            </Button>
          </div>
        </form>

        <div className="text-center mt-8">
          <p className="text-white/70 text-sm">
            ✨ Powered by AI • 📍 Weather Integration • 💾 Auto-saved
          </p>
        </div>
      </div>
    </div>
  );
};