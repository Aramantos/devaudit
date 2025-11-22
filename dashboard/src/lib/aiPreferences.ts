/**
 * AI Preferences Manager
 *
 * Allows users to exclude specific auditors from AI analysis.
 * Results are still shown in dashboard, just not sent to AI for recommendations.
 */

const AI_PREFERENCES_KEY = 'devaudit_ai_preferences';

export interface AIPreferences {
  ignoredAuditors: string[];
  acknowledgedRisk: boolean; // User must acknowledge they understand the risks
}

const DEFAULT_PREFERENCES: AIPreferences = {
  ignoredAuditors: [],
  acknowledgedRisk: false,
};

/**
 * Get user's AI preferences from localStorage
 */
export function getAIPreferences(): AIPreferences {
  if (typeof window === 'undefined') return DEFAULT_PREFERENCES;

  try {
    const stored = localStorage.getItem(AI_PREFERENCES_KEY);
    if (!stored) return DEFAULT_PREFERENCES;

    const parsed = JSON.parse(stored);
    return {
      ignoredAuditors: Array.isArray(parsed.ignoredAuditors) ? parsed.ignoredAuditors : [],
      acknowledgedRisk: parsed.acknowledgedRisk === true,
    };
  } catch (error) {
    console.error('Failed to load AI preferences:', error);
    return DEFAULT_PREFERENCES;
  }
}

/**
 * Save AI preferences to localStorage
 */
export function saveAIPreferences(preferences: AIPreferences): void {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem(AI_PREFERENCES_KEY, JSON.stringify(preferences));
  } catch (error) {
    console.error('Failed to save AI preferences:', error);
  }
}

/**
 * Add an auditor to the ignore list
 */
export function ignoreAuditor(auditorName: string): void {
  const prefs = getAIPreferences();
  if (!prefs.ignoredAuditors.includes(auditorName)) {
    prefs.ignoredAuditors.push(auditorName);
    saveAIPreferences(prefs);
  }
}

/**
 * Remove an auditor from the ignore list
 */
export function unignoreAuditor(auditorName: string): void {
  const prefs = getAIPreferences();
  prefs.ignoredAuditors = prefs.ignoredAuditors.filter(name => name !== auditorName);
  saveAIPreferences(prefs);
}

/**
 * Check if an auditor is ignored
 */
export function isAuditorIgnored(auditorName: string): boolean {
  const prefs = getAIPreferences();
  return prefs.ignoredAuditors.includes(auditorName);
}

/**
 * Acknowledge the risk of ignoring warnings
 */
export function acknowledgeRisk(): void {
  const prefs = getAIPreferences();
  prefs.acknowledgedRisk = true;
  saveAIPreferences(prefs);
}

/**
 * Filter scan results to exclude ignored auditors before sending to AI
 */
export function filterScanResultsForAI(scanResults: any): any {
  const prefs = getAIPreferences();

  if (prefs.ignoredAuditors.length === 0) {
    return scanResults; // No filtering needed
  }

  // Create a copy of scan results without ignored auditors
  const filtered = {
    ...scanResults,
    results: { ...scanResults.results },
  };

  // Remove ignored auditors from results
  prefs.ignoredAuditors.forEach(auditorName => {
    delete filtered.results[auditorName];
  });

  // Recalculate summary to exclude ignored auditors
  if (filtered.summary && filtered.summary.risk_counts) {
    const recalculatedRiskCounts = {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      none: 0,
    };

    Object.values(filtered.results).forEach((result: any) => {
      if (result && result.risk_level) {
        const level = result.risk_level.toLowerCase();
        if (level in recalculatedRiskCounts) {
          recalculatedRiskCounts[level as keyof typeof recalculatedRiskCounts]++;
        }
      }
    });

    filtered.summary = {
      ...filtered.summary,
      risk_counts: recalculatedRiskCounts,
    };
  }

  return filtered;
}

/**
 * Get list of all available auditors from scan results
 */
export function getAvailableAuditors(scanResults: any): string[] {
  if (!scanResults || !scanResults.results) return [];

  return Object.keys(scanResults.results).filter(name => {
    const result = scanResults.results[name];
    return result && result.installed !== false;
  });
}
