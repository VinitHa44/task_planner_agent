import React, { useState, useEffect } from 'react';
import { ErrorHandler } from '../services/errorHandler';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { Button } from './ui/button';
import { X, RefreshCw } from 'lucide-react';

interface ErrorNotificationProps {
  error: any;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

export const ErrorNotification: React.FC<ErrorNotificationProps> = ({
  error,
  onRetry,
  onDismiss,
  className = ''
}) => {
  const [countdown, setCountdown] = useState<number | null>(null);
  const errorInfo = ErrorHandler.getErrorMessage(error);
  const icon = ErrorHandler.getErrorIcon(errorInfo.type);
  const showRetry = ErrorHandler.shouldShowRetry(errorInfo.type);
  
  // Initialize countdown if retry_after is provided
  useEffect(() => {
    if (errorInfo.retryAfter) {
      setCountdown(errorInfo.retryAfter);
      
      const timer = setInterval(() => {
        setCountdown(prev => {
          if (prev === null || prev <= 1) {
            clearInterval(timer);
            return null;
          }
          return prev - 1;
        });
      }, 1000);
      
      return () => clearInterval(timer);
    }
  }, [errorInfo.retryAfter]);

  const handleRetry = () => {
    if (countdown && countdown > 0) return;
    onRetry?.();
  };

  const isRetryDisabled = countdown !== null && countdown > 0;

  return (
    <Alert className={`border-red-200 bg-red-50 ${className}`}>
      <div className="flex items-start gap-3">
        <div className="text-2xl">{icon}</div>
        
        <div className="flex-1">
          <AlertTitle className="text-red-800 mb-2">
            Something went wrong
          </AlertTitle>
          
          <AlertDescription className="text-red-700 mb-3">
            {errorInfo.message}
          </AlertDescription>
          
          {countdown !== null && countdown > 0 && (
            <div className="text-sm text-red-600 mb-3 font-medium">
              You can try again in {ErrorHandler.formatRetryTime(countdown)}
            </div>
          )}
          
          {showRetry && onRetry && (
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={handleRetry}
                disabled={isRetryDisabled}
                className="border-red-300 text-red-700 hover:bg-red-100"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                {isRetryDisabled 
                  ? `Retry in ${ErrorHandler.formatRetryTime(countdown!)}`
                  : 'Try Again'
                }
              </Button>
            </div>
          )}
        </div>
        
        {onDismiss && (
          <Button
            size="sm"
            variant="ghost"
            onClick={onDismiss}
            className="text-red-500 hover:text-red-700 hover:bg-red-100 p-1"
          >
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>
    </Alert>
  );
};