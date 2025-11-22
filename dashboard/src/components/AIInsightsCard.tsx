'use client';

import { useState, useEffect } from 'react';
import { Sparkles, AlertCircle, TrendingUp, Shield, Loader2, Info, Settings } from 'lucide-react';
import AIPreferencesModal from './AIPreferencesModal';
import { getAIPreferences, filterScanResultsForAI } from '@/lib/aiPreferences';

interface AIRecommendations {
  priority_action: string;
  recommendations: string[];
  security_score: number;
  risk_summary: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  color: string;
  model: string;
}

interface AIInsightsCardProps {
  scanId?: string;
  scanResults?: any;
}

export default function AIInsightsCard({ scanId, scanResults }: AIInsightsCardProps) {
  const [recommendations, setRecommendations] = useState<AIRecommendations | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiAvailable, setAiAvailable] = useState(false);
  const [aiConfigured, setAiConfigured] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [ignoredCount, setIgnoredCount] = useState(0);

  // Check if AI is available on mount
  useEffect(() => {
    checkAIStatus();
    updateIgnoredCount();
  }, []);

  const updateIgnoredCount = () => {
    const prefs = getAIPreferences();
    setIgnoredCount(prefs.ignoredAuditors.length);
  };

  const checkAIStatus = async () => {
    try {
      const response = await fetch('/api/ai/status');
      const data = await response.json();
      setAiAvailable(data.available);
      setAiConfigured(data.configured);
    } catch (err) {
      console.error('Failed to check AI status:', err);
    }
  };

  const analyzeWithAI = async () => {
    setLoading(true);
    setError(null);

    try {
      // Filter scan results based on user preferences
      const filteredResults = scanResults ? filterScanResultsForAI(scanResults) : undefined;

      const response = await fetch('/api/ai/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scan_id: scanId,
          scan_results: filteredResults,
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        setRecommendations(data.recommendations);
      } else {
        setError(data.message || 'AI analysis failed');
      }
    } catch (err) {
      setError('Failed to connect to AI service');
      console.error('AI analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Show install prompt if AI not available
  if (!aiAvailable) {
    return (
      <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-700/50 p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-blue-500/10 rounded-lg">
            <Sparkles className="w-6 h-6 text-blue-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white mb-2">AI-Powered Insights</h3>
            <p className="text-gray-400 text-sm mb-4">
              Get intelligent security recommendations powered by Gemini. Install the AI package to enable this feature.
            </p>
            <div className="bg-gray-800/80 rounded-lg p-4 border border-gray-700/50">
              <code className="text-emerald-400 text-sm font-mono">
                pip install &apos;devaudit[ai]&apos;
              </code>
            </div>
            <p className="text-xs text-gray-500 mt-3">
              Privacy note: AI analysis uses your own Google Cloud project. No data is sent to third parties.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Show configure prompt if AI available but not configured
  if (aiAvailable && !aiConfigured) {
    return (
      <div className="bg-gradient-to-br from-yellow-900/20 to-yellow-800/20 backdrop-blur-sm rounded-lg border border-yellow-700/50 p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-yellow-500/10 rounded-lg">
            <Info className="w-6 h-6 text-yellow-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white mb-2">Configure Vertex AI</h3>
            <p className="text-gray-400 text-sm mb-4">
              Vertex AI SDK is installed but not configured. Set up your Google Cloud credentials to enable AI insights.
            </p>
            <div className="bg-gray-800/80 rounded-lg p-4 border border-gray-700/50 space-y-2">
              <code className="text-emerald-400 text-sm font-mono block">
                gcloud auth application-default login
              </code>
              <p className="text-xs text-gray-500">Or set GOOGLE_APPLICATION_CREDENTIALS environment variable</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show analyze button if no recommendations yet
  if (!recommendations && !loading) {
    return (
      <>
        <div className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 backdrop-blur-sm rounded-lg border border-blue-700/50 p-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-4 flex-1">
              <div className="p-3 bg-blue-500/10 rounded-lg">
                <Sparkles className="w-6 h-6 text-blue-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white mb-2">AI Security Insights</h3>
                <p className="text-gray-400 text-sm mb-4">
                  Get intelligent, context-aware security recommendations powered by Gemini 2.0 Flash.
                </p>
                {ignoredCount > 0 && (
                  <p className="text-xs text-orange-400 mb-3">
                    {ignoredCount} {ignoredCount === 1 ? 'auditor' : 'auditors'} excluded from analysis
                  </p>
                )}
                <button
                  onClick={analyzeWithAI}
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white rounded-lg font-medium transition-all duration-200 flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  Analyze with AI
                </button>
              </div>
            </div>
            <button
              onClick={() => setShowPreferences(true)}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors flex-shrink-0"
              title="AI Preferences"
            >
              <Settings className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>
        <AIPreferencesModal
          isOpen={showPreferences}
          onClose={() => setShowPreferences(false)}
          scanResults={scanResults}
          onPreferencesChanged={() => {
            updateIgnoredCount();
            setRecommendations(null); // Clear recommendations to force re-analysis
          }}
        />
      </>
    );
  }

  // Show loading state
  if (loading) {
    return (
      <div className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 backdrop-blur-sm rounded-lg border border-blue-700/50 p-6">
        <div className="flex items-center justify-center gap-3 py-8">
          <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
          <span className="text-gray-300">Analyzing with AI...</span>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="bg-gradient-to-br from-red-900/20 to-red-800/20 backdrop-blur-sm rounded-lg border border-red-700/50 p-6">
        <div className="flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white mb-2">AI Analysis Failed</h3>
            <p className="text-gray-400 text-sm mb-3">{error}</p>
            <button
              onClick={analyzeWithAI}
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show recommendations
  if (!recommendations) return null;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreGradient = (score: number) => {
    if (score >= 80) return 'from-emerald-500 to-green-500';
    if (score >= 60) return 'from-yellow-500 to-orange-500';
    if (score >= 40) return 'from-orange-500 to-red-500';
    return 'from-red-500 to-red-600';
  };

  return (
    <>
      <div className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 backdrop-blur-sm rounded-lg border border-blue-700/50 p-6 space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">AI Security Insights</h3>
              <p className="text-xs text-gray-400">Powered by {recommendations.model}</p>
              {ignoredCount > 0 && (
                <p className="text-xs text-orange-400 mt-1">
                  {ignoredCount} {ignoredCount === 1 ? 'auditor' : 'auditors'} excluded
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Settings Button */}
            <button
              onClick={() => setShowPreferences(true)}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              title="AI Preferences"
            >
              <Settings className="w-5 h-5 text-gray-400" />
            </button>

            {/* Security Score */}
            <div className="text-center">
          <div className={`text-3xl font-bold ${getScoreColor(recommendations.security_score)}`}>
            {recommendations.security_score}
          </div>
          <div className="text-xs text-gray-400 mt-1">Security Score</div>
          {/* Score bar */}
          <div className="w-20 h-1.5 bg-gray-700 rounded-full mt-2 overflow-hidden">
            <div
              className={`h-full bg-gradient-to-r ${getScoreGradient(recommendations.security_score)} transition-all duration-500`}
              style={{ width: `${recommendations.security_score}%` }}
            />
          </div>
        </div>
      </div>

      {/* Risk Summary */}
      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
        <div className="flex items-start gap-3">
          <Shield className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <div className="text-sm font-medium text-gray-300 mb-1">Risk Summary</div>
            <div className="text-sm text-gray-400">{recommendations.risk_summary}</div>
          </div>
        </div>
      </div>

      {/* Priority Action */}
      <div className="bg-gradient-to-r from-orange-900/30 to-red-900/30 rounded-lg p-4 border border-orange-700/50">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" />
          <div>
            <div className="text-sm font-semibold text-orange-300 mb-1">Priority Action</div>
            <div className="text-sm text-gray-300">{recommendations.priority_action}</div>
          </div>
        </div>
      </div>

      {/* Top Recommendations */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp className="w-4 h-4 text-blue-400" />
          <h4 className="text-sm font-semibold text-gray-300">Top Recommendations</h4>
        </div>
        <div className="space-y-2">
          {recommendations.recommendations.map((rec, index) => (
            <div
              key={index}
              className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50 hover:border-blue-600/50 transition-colors"
            >
              <div className="flex items-start gap-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 text-xs font-semibold flex-shrink-0">
                  {index + 1}
                </span>
                <p className="text-sm text-gray-300 flex-1">{rec}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Refresh Button */}
      <button
        onClick={analyzeWithAI}
        disabled={loading}
        className="w-full px-4 py-2 bg-gray-800/80 hover:bg-gray-700/80 text-gray-300 rounded-lg text-sm font-medium transition-all duration-200 border border-gray-700/50 hover:border-blue-600/50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Refresh AI Analysis
      </button>
      </div>

      {/* Preferences Modal */}
      <AIPreferencesModal
        isOpen={showPreferences}
        onClose={() => setShowPreferences(false)}
        scanResults={scanResults}
        onPreferencesChanged={() => {
          updateIgnoredCount();
          setRecommendations(null); // Clear recommendations to force re-analysis
        }}
      />
    </>
  );
}
