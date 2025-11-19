import { useState, useEffect } from 'react';
import { GitCompare, TrendingUp, TrendingDown, Plus, Minus, Calendar, X, Shield, Package, AlertTriangle } from 'lucide-react';
import { Modal } from './Modal';

interface ComparisonData {
  scan1: {
    id: string;
    timestamp: string;
  };
  scan2: {
    id: string;
    timestamp: string;
  };
  changes: {
    packages: {
      added: string[];
      removed: string[];
    };
    vulnerabilities: {
      added: any[];
      fixed: any[];
    };
    outdated: {
      added: any[];
      fixed: any[];
    };
  };
  summary: {
    new_packages: number;
    removed_packages: number;
    new_vulnerabilities: number;
    fixed_vulnerabilities: number;
    newly_outdated: number;
    updated_packages: number;
  };
}

interface ComparisonViewProps {
  scanId1: string;
  scanId2: string;
  isOpen: boolean;
  onClose: () => void;
}

export function ComparisonView({ scanId1, scanId2, isOpen, onClose }: ComparisonViewProps) {
  const [comparison, setComparison] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && scanId1 && scanId2) {
      loadComparison();
    }
  }, [isOpen, scanId1, scanId2]);

  const loadComparison = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/history/compare/${scanId1}/${scanId2}`);
      const data = await response.json();

      if (response.ok && data.comparison) {
        setComparison(data.comparison);
      } else {
        setError(data.message || 'Failed to load comparison');
      }
    } catch (err) {
      setError('Failed to fetch comparison data');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getOverallTrend = () => {
    if (!comparison) return null;

    const { summary } = comparison;
    const improvements = summary.fixed_vulnerabilities + summary.updated_packages;
    const regressions = summary.new_vulnerabilities + summary.newly_outdated;

    if (improvements > regressions) {
      return { type: 'positive', icon: TrendingDown, text: 'Environment Improved', color: 'text-primary-600 dark:text-primary-400' };
    } else if (regressions > improvements) {
      return { type: 'negative', icon: TrendingUp, text: 'Environment Degraded', color: 'text-red-600 dark:text-red-400' };
    }
    return { type: 'neutral', icon: GitCompare, text: 'No Significant Change', color: 'text-gray-600 dark:text-gray-400' };
  };

  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Scan Comparison">
      {loading ? (
        <div className="space-y-6 animate-pulse">
          {/* Timeline Skeleton */}
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-gray-200 dark:bg-dark-600 rounded"></div>
              <div>
                <div className="h-3 w-16 bg-gray-200 dark:bg-dark-600 rounded mb-1"></div>
                <div className="h-4 w-32 bg-gray-200 dark:bg-dark-600 rounded"></div>
              </div>
            </div>
            <div className="w-5 h-5 bg-gray-200 dark:bg-dark-600 rounded"></div>
            <div className="flex items-center gap-2">
              <div>
                <div className="h-3 w-16 bg-gray-200 dark:bg-dark-600 rounded mb-1"></div>
                <div className="h-4 w-32 bg-gray-200 dark:bg-dark-600 rounded"></div>
              </div>
              <div className="w-4 h-4 bg-gray-200 dark:bg-dark-600 rounded"></div>
            </div>
          </div>

          {/* Trend Skeleton */}
          <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg border border-gray-200 dark:border-dark-600">
            <div className="h-5 w-48 bg-gray-200 dark:bg-dark-600 rounded mb-2"></div>
            <div className="h-3 w-64 bg-gray-200 dark:bg-dark-600 rounded"></div>
          </div>

          {/* Stats Skeleton */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-3 bg-gray-50 dark:bg-dark-700 rounded-lg border border-gray-200 dark:border-dark-600">
                <div className="h-4 w-24 bg-gray-200 dark:bg-dark-600 rounded mb-2"></div>
                <div className="h-6 w-16 bg-gray-200 dark:bg-dark-600 rounded"></div>
              </div>
            ))}
          </div>

          {/* Change Sections Skeleton */}
          {[1, 2].map((i) => (
            <div key={i} className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg border border-gray-200 dark:border-dark-600">
              <div className="h-4 w-40 bg-gray-200 dark:bg-dark-600 rounded mb-2"></div>
              <div className="flex flex-wrap gap-2">
                {[1, 2, 3].map((j) => (
                  <div key={j} className="h-6 w-24 bg-gray-200 dark:bg-dark-600 rounded"></div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      ) : comparison ? (
        <div className="space-y-6">
          {/* Timeline */}
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-500 dark:text-gray-400" />
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Older Scan</p>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {formatDate(comparison.scan1.timestamp)}
                </p>
              </div>
            </div>
            <GitCompare className="w-5 h-5 text-gray-400" />
            <div className="flex items-center gap-2">
              <div className="text-right">
                <p className="text-xs text-gray-500 dark:text-gray-400">Newer Scan</p>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {formatDate(comparison.scan2.timestamp)}
                </p>
              </div>
              <Calendar className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </div>
          </div>

          {/* Overall Trend */}
          {(() => {
            const trend = getOverallTrend();
            if (!trend) return null;
            const TrendIcon = trend.icon;

            return (
              <div className={`flex items-center gap-2 p-4 rounded-lg border ${
                trend.type === 'positive'
                  ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800'
                  : trend.type === 'negative'
                  ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                  : 'bg-gray-50 dark:bg-dark-700 border-gray-200 dark:border-dark-600'
              }`}>
                <TrendIcon className={`w-6 h-6 ${trend.color}`} />
                <div>
                  <p className={`font-semibold ${trend.color}`}>{trend.text}</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                    {comparison.summary.fixed_vulnerabilities + comparison.summary.updated_packages} improvements,{' '}
                    {comparison.summary.new_vulnerabilities + comparison.summary.newly_outdated} regressions
                  </p>
                </div>
              </div>
            );
          })()}

          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            <StatChange
              icon={<Shield className="w-4 h-4" />}
              label="Vulnerabilities"
              added={comparison.summary.new_vulnerabilities}
              removed={comparison.summary.fixed_vulnerabilities}
            />
            <StatChange
              icon={<AlertTriangle className="w-4 h-4" />}
              label="Outdated"
              added={comparison.summary.newly_outdated}
              removed={comparison.summary.updated_packages}
            />
            <StatChange
              icon={<Package className="w-4 h-4" />}
              label="Packages"
              added={comparison.summary.new_packages}
              removed={comparison.summary.removed_packages}
            />
          </div>

          {/* Detailed Changes */}
          <div className="space-y-4">
            {/* Fixed Vulnerabilities */}
            {comparison.changes.vulnerabilities.fixed.length > 0 && (
              <ChangeSection
                title="✅ Fixed Vulnerabilities"
                items={comparison.changes.vulnerabilities.fixed.map(v => v.package)}
                type="positive"
              />
            )}

            {/* New Vulnerabilities */}
            {comparison.changes.vulnerabilities.added.length > 0 && (
              <ChangeSection
                title="⚠️ New Vulnerabilities"
                items={comparison.changes.vulnerabilities.added.map(v => v.package)}
                type="negative"
              />
            )}

            {/* Updated Packages */}
            {comparison.changes.outdated.fixed.length > 0 && (
              <ChangeSection
                title="⬆️ Updated Packages"
                items={comparison.changes.outdated.fixed.map(p => p.name)}
                type="positive"
              />
            )}

            {/* Newly Outdated */}
            {comparison.changes.outdated.added.length > 0 && (
              <ChangeSection
                title="📦 Newly Outdated"
                items={comparison.changes.outdated.added.map(p => p.name)}
                type="warning"
              />
            )}

            {/* Added Packages */}
            {comparison.changes.packages.added.length > 0 && (
              <ChangeSection
                title="➕ Added Packages"
                items={comparison.changes.packages.added}
                type="neutral"
              />
            )}

            {/* Removed Packages */}
            {comparison.changes.packages.removed.length > 0 && (
              <ChangeSection
                title="➖ Removed Packages"
                items={comparison.changes.packages.removed}
                type="neutral"
              />
            )}
          </div>
        </div>
      ) : null}
    </Modal>
  );
}

function StatChange({ icon, label, added, removed }: { icon: React.ReactNode; label: string; added: number; removed: number }) {
  return (
    <div className="p-3 bg-gray-50 dark:bg-dark-700 rounded-lg border border-gray-200 dark:border-dark-600">
      <div className="flex items-center gap-2 mb-2">
        <div className="text-gray-600 dark:text-gray-400">{icon}</div>
        <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{label}</span>
      </div>
      <div className="flex items-center gap-3 text-sm">
        {added > 0 && (
          <div className="flex items-center gap-1">
            <Plus className="w-3 h-3 text-red-600 dark:text-red-400" />
            <span className="font-semibold text-red-600 dark:text-red-400">{added}</span>
          </div>
        )}
        {removed > 0 && (
          <div className="flex items-center gap-1">
            <Minus className="w-3 h-3 text-primary-600 dark:text-primary-400" />
            <span className="font-semibold text-primary-600 dark:text-primary-400">{removed}</span>
          </div>
        )}
        {added === 0 && removed === 0 && (
          <span className="text-gray-500 dark:text-gray-400 text-xs">No change</span>
        )}
      </div>
    </div>
  );
}

function ChangeSection({ title, items, type }: { title: string; items: string[]; type: 'positive' | 'negative' | 'warning' | 'neutral' }) {
  const colors = {
    positive: 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800 text-primary-700 dark:text-primary-300',
    negative: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300',
    warning: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-700 dark:text-yellow-300',
    neutral: 'bg-gray-50 dark:bg-dark-700 border-gray-200 dark:border-dark-600 text-gray-700 dark:text-gray-300',
  };

  return (
    <div className={`p-4 rounded-lg border ${colors[type]}`}>
      <h4 className="font-semibold mb-2 text-sm">{title}</h4>
      <div className="flex flex-wrap gap-2">
        {items.slice(0, 10).map((item, idx) => (
          <span
            key={idx}
            className="px-2 py-1 bg-white/50 dark:bg-black/20 rounded text-xs font-mono border border-current/20"
          >
            {item}
          </span>
        ))}
        {items.length > 10 && (
          <span className="px-2 py-1 text-xs">
            +{items.length - 10} more
          </span>
        )}
      </div>
    </div>
  );
}
