'use client';

import { useState, useEffect } from 'react';
import { X, AlertTriangle, Settings } from 'lucide-react';
import {
  getAIPreferences,
  saveAIPreferences,
  getAvailableAuditors,
  type AIPreferences,
} from '@/lib/aiPreferences';

interface AIPreferencesModalProps {
  isOpen: boolean;
  onClose: () => void;
  scanResults: any;
  onPreferencesChanged: () => void;
}

export default function AIPreferencesModal({
  isOpen,
  onClose,
  scanResults,
  onPreferencesChanged,
}: AIPreferencesModalProps) {
  const [preferences, setPreferences] = useState<AIPreferences>({
    ignoredAuditors: [],
    acknowledgedRisk: false,
  });
  const [availableAuditors, setAvailableAuditors] = useState<string[]>([]);
  const [showWarning, setShowWarning] = useState(false);

  useEffect(() => {
    if (isOpen) {
      const prefs = getAIPreferences();
      setPreferences(prefs);
      setShowWarning(!prefs.acknowledgedRisk && prefs.ignoredAuditors.length === 0);

      const auditors = getAvailableAuditors(scanResults);
      setAvailableAuditors(auditors);
    }
  }, [isOpen, scanResults]);

  if (!isOpen) return null;

  const handleToggleAuditor = (auditorName: string) => {
    const newIgnored = preferences.ignoredAuditors.includes(auditorName)
      ? preferences.ignoredAuditors.filter(name => name !== auditorName)
      : [...preferences.ignoredAuditors, auditorName];

    const newPrefs = {
      ...preferences,
      ignoredAuditors: newIgnored,
    };

    setPreferences(newPrefs);
  };

  const handleAcknowledgeRisk = () => {
    const newPrefs = {
      ...preferences,
      acknowledgedRisk: true,
    };
    setPreferences(newPrefs);
    setShowWarning(false);
  };

  const handleSave = () => {
    saveAIPreferences(preferences);
    onPreferencesChanged();
    onClose();
  };

  const handleCancel = () => {
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-lg border border-gray-700 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gray-900 border-b border-gray-700 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Settings className="w-5 h-5 text-blue-400" />
            <h2 className="text-xl font-semibold text-white">AI Analysis Preferences</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-800 rounded transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Warning Banner - First Time */}
        {showWarning && (
          <div className="m-4 p-4 bg-red-900/20 border border-red-700/50 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold text-red-300 mb-2">Important Warning</h3>
                <p className="text-sm text-gray-300 mb-3">
                  <strong>We do NOT recommend ignoring any security warnings.</strong> Each
                  auditor provides important insights about your system's security posture.
                  Ignoring warnings may leave you vulnerable to:
                </p>
                <ul className="text-sm text-gray-300 space-y-1 mb-4 ml-4 list-disc">
                  <li>Data loss from hardware failure or malware</li>
                  <li>Security breaches from outdated software</li>
                  <li>System instability from driver issues</li>
                  <li>Compliance violations</li>
                </ul>
                <p className="text-sm text-gray-300 mb-4">
                  This feature only filters what the AI analyzes. The audit results will still be
                  visible in your dashboard. <strong>Use this feature at your own risk.</strong>
                </p>
                <button
                  onClick={handleAcknowledgeRisk}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors"
                >
                  I Understand the Risks
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Persistent Acknowledgment - Show when user has previously agreed */}
        {!showWarning && preferences.acknowledgedRisk && (
          <div className="m-4 p-3 bg-orange-900/20 border border-orange-700/50 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-xs text-orange-300">
                  <strong>Previously Acknowledged:</strong> You have accepted the risks of ignoring security warnings.
                  This feature filters AI analysis only—audit results remain visible in the dashboard.
                  {' '}
                  <button
                    onClick={() => {
                      setShowWarning(true);
                      const newPrefs = { ...preferences, acknowledgedRisk: false, ignoredAuditors: [] };
                      setPreferences(newPrefs);
                    }}
                    className="underline hover:text-orange-200 transition-colors"
                  >
                    Reset preferences
                  </button>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="p-4">
          <p className="text-gray-400 text-sm mb-4">
            Select which auditors to exclude from AI analysis. Audit results will still appear in
            your dashboard, but the AI won't generate recommendations for these items.
          </p>

          {/* Auditors List */}
          <div className="space-y-2">
            {availableAuditors.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No scan results available. Run a scan first.</p>
              </div>
            ) : (
              availableAuditors.map(auditorName => {
                const isIgnored = preferences.ignoredAuditors.includes(auditorName);
                const isDisabled = !preferences.acknowledgedRisk && !isIgnored;

                return (
                  <div
                    key={auditorName}
                    className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                      isIgnored
                        ? 'bg-gray-800/50 border-gray-600'
                        : 'bg-gray-800/30 border-gray-700/50 hover:border-blue-600/50'
                    } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <label
                      htmlFor={`auditor-${auditorName}`}
                      className="flex items-center gap-3 flex-1 cursor-pointer"
                    >
                      <input
                        id={`auditor-${auditorName}`}
                        type="checkbox"
                        checked={isIgnored}
                        onChange={() => handleToggleAuditor(auditorName)}
                        disabled={isDisabled}
                        className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-0 disabled:cursor-not-allowed"
                      />
                      <span className="text-gray-300 font-medium">{auditorName}</span>
                    </label>
                    {isIgnored && (
                      <span className="text-xs text-orange-400 bg-orange-900/30 px-2 py-1 rounded">
                        Ignored
                      </span>
                    )}
                  </div>
                );
              })
            )}
          </div>

          {/* Summary */}
          {preferences.ignoredAuditors.length > 0 && (
            <div className="mt-4 p-3 bg-blue-900/20 border border-blue-700/50 rounded-lg">
              <p className="text-sm text-blue-300">
                <strong>{preferences.ignoredAuditors.length}</strong>{' '}
                {preferences.ignoredAuditors.length === 1 ? 'auditor' : 'auditors'} will be
                excluded from AI analysis
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-900 border-t border-gray-700 p-4 flex items-center justify-between">
          <button
            onClick={() => {
              setPreferences({ ignoredAuditors: [], acknowledgedRisk: preferences.acknowledgedRisk });
            }}
            className="text-sm text-gray-400 hover:text-gray-300 transition-colors"
            disabled={preferences.ignoredAuditors.length === 0}
          >
            Clear All
          </button>
          <div className="flex gap-3">
            <button
              onClick={handleCancel}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-sm font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Save Preferences
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
