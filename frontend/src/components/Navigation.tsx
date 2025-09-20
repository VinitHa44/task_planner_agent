import { Button } from "@/components/ui/button";
import { Sparkles, History, Home } from "lucide-react";

interface NavigationProps {
  currentView: 'home' | 'plan' | 'history';
  onNavigate: (view: 'home' | 'plan' | 'history') => void;
  planCount?: number;
}

export const Navigation = ({ currentView, onNavigate, planCount = 0 }: NavigationProps) => {
  return (
    <nav className="bg-white/95 backdrop-blur-sm border-b sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="bg-gradient-to-r from-primary to-secondary rounded-lg p-2">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text">
              PlanGenius
            </span>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center gap-2">
            <Button
              variant={currentView === 'home' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => onNavigate('home')}
              className="flex items-center gap-2"
            >
              <Home className="w-4 h-4" />
              <span className="hidden sm:inline">New Plan</span>
            </Button>
            
            <Button
              variant={currentView === 'history' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => onNavigate('history')}
              className="flex items-center gap-2"
            >
              <History className="w-4 h-4" />
              <span className="hidden sm:inline">
                History {planCount > 0 && `(${planCount})`}
              </span>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};