"use client"

import React, { useState, useEffect, useRef } from 'react';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle2, XCircle, Loader2, Upload, Sparkles, Server } from 'lucide-react';
import { buildApiUrl } from '@/lib/api';

interface ProgressData {
  overall_progress: number;
  current_stage: string;
  stage_progress: number;
  message: string;
  details?: any;
  timestamp: number;
  completed?: boolean;
  error?: string;
}

interface PDFProgressTrackerProps {
  sessionId: string;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
  onFieldUpdate?: (fieldName: string, fieldValue: any) => void;
  className?: string;
}

const stageIcons: { [key: string]: React.ElementType } = {
  upload: Upload,
  processing: Sparkles,
};

const stageTitles: { [key: string]: string } = {
  upload: "File Upload",
  processing: "Document Processing",
};

export default function PDFProgressTracker({ 
  sessionId, 
  onComplete, 
  onError, 
  onFieldUpdate,
  className = "" 
}: PDFProgressTrackerProps) {
  const [progressData, setProgressData] = useState<ProgressData | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [pollingError, setPollingError] = useState<string | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastFieldUpdatesRef = useRef<Set<string>>(new Set());

  const pollProgress = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(buildApiUrl(`/pdf-progress/${sessionId}`));
      
      if (!response.ok) {
        if (response.status === 404) {
          // Session not found yet, keep polling
          return;
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Progress update received:', data);
      
      setProgressData(data);
      setPollingError(null);

      // Check for field updates
      if (data.field_updates) {
        for (const [fieldName, fieldValue] of Object.entries(data.field_updates)) {
          const updateKey = `${fieldName}-${JSON.stringify(fieldValue)}`;
          if (!lastFieldUpdatesRef.current.has(updateKey)) {
            console.log('Field update received:', fieldName, fieldValue);
            onFieldUpdate?.(fieldName, fieldValue);
            lastFieldUpdatesRef.current.add(updateKey);
          }
        }
      }

      // Check for completion
      if (data.completed) {
        console.log('Processing completed');
        onComplete?.(data.result);
        stopPolling();
      }

      // Check for error
      if (data.error) {
        console.error('Processing error:', data.error);
        onError?.(data.error);
        stopPolling();
      }

    } catch (error) {
      console.error('Progress polling error:', error);
      setPollingError(error instanceof Error ? error.message : 'Unknown error');
    }
  };

  const startPolling = () => {
    if (pollingIntervalRef.current) return;
    
    setIsPolling(true);
    setPollingError(null);
    
    // Poll immediately
    pollProgress();
    
    // Then poll every 1 second
    pollingIntervalRef.current = setInterval(pollProgress, 1000);
  };

  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
    setIsPolling(false);
  };

  useEffect(() => {
    if (sessionId) {
      startPolling();
    }

    return () => {
      stopPolling();
    };
  }, [sessionId]);

  if (!sessionId) {
    return null;
  }

  const overallProgress = progressData?.overall_progress || 0;
  const overallMessage = progressData?.message || "Starting PDF processing...";
  const error = progressData?.error || pollingError;
  
  // Show progress bar during PDF processing
  const showProgressBar = true;

  const getStatusIcon = (status: string) => {
    if (status === 'completed') return <CheckCircle2 className="h-5 w-5 text-green-500" />;
    if (status === 'error') return <XCircle className="h-5 w-5 text-red-500" />;
    return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />;
  };

  return (
    <Card className={`w-full ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {getStatusIcon(progressData?.completed ? 'completed' : progressData?.error ? 'error' : 'in_progress')}
          <span>PDF Parsing Progress</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {pollingError && (
          <div className="flex items-center gap-2 text-red-500 mb-4">
            <XCircle className="h-4 w-4" />
            <span>Error: {pollingError}</span>
          </div>
        )}
        
        {showProgressBar ? (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">{overallMessage}</span>
              <span className="text-xs text-gray-500">{overallProgress}%</span>
            </div>
            <Progress value={overallProgress} className="w-full h-2" />
          </div>
        ) : (
          <div className="mb-4">
            <div className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
              <span className="text-sm font-medium text-gray-700">{overallMessage}</span>
            </div>
          </div>
        )}

        {/* Removed individual stage progress bar - only show overall progress */}

        {isPolling && (
          <div className="mt-4 text-xs text-gray-500 flex items-center gap-2">
            <Loader2 className="h-3 w-3 animate-spin" />
            <span>Polling for updates...</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
