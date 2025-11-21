'use client';

import { AlertTriangle, AlertCircle, Info, Loader } from 'lucide-react';

interface ActionsCardProps {
  systemAuditors: any;
  isScanning?: boolean;
}

interface Action {
  auditor: string;
  riskLevel: string;
  message: string;
}

export function ActionsCard({ systemAuditors, isScanning = false }: ActionsCardProps) {
  if (!systemAuditors) {
    return null;
  }

  // If scanning, show scanning state
  if (isScanning) {
    return (
      <div className="bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 rounded-lg border-2 border-amber-200 dark:border-amber-800 p-6">
        <div className="flex items-center gap-3">
          <Loader className="w-6 h-6 text-amber-600 dark:text-amber-400 animate-spin" />
          <div>
            <h3 className="text-lg font-semibold text-amber-900 dark:text-amber-100">
              Analyzing System Security
            </h3>
            <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
              Running comprehensive security audit. Recommendations will appear when complete.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Collect all actions that need attention (MEDIUM or above)
  const actions: Action[] = [];

  Object.entries(systemAuditors).forEach(([name, data]: [string, any]) => {
    if (!data || !data.installed) return;

    const riskLevel = data.risk_level || 'none';

    // Only show MEDIUM, HIGH, or CRITICAL issues
    if (['medium', 'high', 'critical'].includes(riskLevel)) {
      actions.push({
        auditor: name,
        riskLevel: riskLevel,
        message: data.recommendation || 'Action required'
      });
    }
  });

  // If no actions needed, show success state
  if (actions.length === 0) {
    return (
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border-2 border-green-200 dark:border-green-800 p-6">
        <div className="flex items-center gap-3">
          <Info className="w-6 h-6 text-green-600 dark:text-green-400" />
          <div>
            <h3 className="text-lg font-semibold text-green-900 dark:text-green-100">
              All Systems Healthy
            </h3>
            <p className="text-sm text-green-700 dark:text-green-300 mt-1">
              No immediate actions required. Continue monitoring your system security.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Sort by risk level (critical first, then high, then medium)
  const riskOrder = { critical: 0, high: 1, medium: 2 };
  actions.sort((a, b) => {
    return (riskOrder[a.riskLevel as keyof typeof riskOrder] || 999) -
           (riskOrder[b.riskLevel as keyof typeof riskOrder] || 999);
  });

  const getRiskColor = (riskLevel: string) => {
    const colors = {
      critical: {
        bg: 'bg-red-50 dark:bg-red-900/20',
        border: 'border-red-200 dark:border-red-800',
        text: 'text-red-700 dark:text-red-300',
        badge: 'bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-200'
      },
      high: {
        bg: 'bg-orange-50 dark:bg-orange-900/20',
        border: 'border-orange-200 dark:border-orange-800',
        text: 'text-orange-700 dark:text-orange-300',
        badge: 'bg-orange-100 dark:bg-orange-900/40 text-orange-800 dark:text-orange-200'
      },
      medium: {
        bg: 'bg-yellow-50 dark:bg-yellow-900/20',
        border: 'border-yellow-200 dark:border-yellow-800',
        text: 'text-yellow-700 dark:text-yellow-300',
        badge: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-200'
      }
    };
    return colors[riskLevel as keyof typeof colors] || colors.medium;
  };

  // Count by risk level
  const criticalCount = actions.filter(a => a.riskLevel === 'critical').length;
  const highCount = actions.filter(a => a.riskLevel === 'high').length;
  const mediumCount = actions.filter(a => a.riskLevel === 'medium').length;

  return (
    <div className="bg-white dark:bg-dark-800 rounded-lg border-2 border-gray-200 dark:border-dark-700 shadow-md">
      {/* Header */}
      <div className="p-6 border-b-2 border-gray-200 dark:border-dark-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Recommended Actions
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {actions.length} issue{actions.length > 1 ? 's' : ''} requiring attention
              </p>
            </div>
          </div>

          {/* Risk count badges - text hidden on mobile */}
          <div className="flex gap-2">
            {criticalCount > 0 && (
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-200">
                {criticalCount}<span className="hidden md:inline"> CRITICAL</span>
              </span>
            )}
            {highCount > 0 && (
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-orange-100 dark:bg-orange-900/40 text-orange-800 dark:text-orange-200">
                {highCount}<span className="hidden md:inline"> HIGH</span>
              </span>
            )}
            {mediumCount > 0 && (
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-200">
                {mediumCount}<span className="hidden md:inline"> MEDIUM</span>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Actions List */}
      <div className="p-6 space-y-4">
        {actions.map((action, index) => {
          const colors = getRiskColor(action.riskLevel);

          return (
            <div
              key={index}
              className={`rounded-lg border-2 ${colors.border} ${colors.bg} p-4 transition-all hover:shadow-md`}
            >
              <div className="flex items-start gap-3">
                <AlertCircle className={`w-5 h-5 mt-0.5 flex-shrink-0 ${colors.text}`} />
                <div className="flex-grow min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold text-gray-900 dark:text-gray-100">
                      {action.auditor}
                    </h4>
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${colors.badge}`}>
                      {action.riskLevel}
                    </span>
                  </div>
                  <p className={`text-sm ${colors.text} leading-relaxed`}>
                    {action.message}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
