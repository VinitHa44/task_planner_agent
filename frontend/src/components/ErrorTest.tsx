import React from 'react';
import { ErrorNotification } from './ErrorNotification';

// Test component to verify error handling
export const ErrorTest: React.FC = () => {
  const quotaError = {
    error: {
      type: 'QUOTA_EXCEEDED',
      message: 'AI service quota exceeded. Please try again later.',
      technical_details: '429 You exceeded your current quota',
      retry_after: 18
    }
  };

  const networkError = {
    error: {
      type: 'NETWORK_ERROR',
      message: 'Network connection issue. Please check your internet and try again.',
      technical_details: 'Failed to fetch'
    }
  };

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold">Error Handling Test</h2>
      
      <div>
        <h3 className="text-lg font-semibold mb-2">Quota Exceeded Error</h3>
        <ErrorNotification 
          error={quotaError}
          onRetry={() => console.log('Retry clicked')}
          onDismiss={() => console.log('Dismiss clicked')}
        />
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-2">Network Error</h3>
        <ErrorNotification 
          error={networkError}
          onRetry={() => console.log('Retry clicked')}
          onDismiss={() => console.log('Dismiss clicked')}
        />
      </div>
    </div>
  );
};