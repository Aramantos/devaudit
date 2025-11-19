import { Shield, AlertTriangle, CheckCircle, Info, Cpu, HelpCircle } from 'lucide-react';
import { useState } from 'react';
import { Modal } from './Modal';

interface SystemSecurityCardProps {
  data: any;
}

interface SystemAuditor {
  name: string;
  installed: boolean;
  version?: string;
  risk_level?: string;
  recommendation?: string;
  age_days?: number;
  vendor?: string;
  release_date?: string;
  educational_content?: {
    what_is_it: string;
    why_it_matters: string;
    when_to_update: string;
    when_to_skip: string;
    how_to_fix: string;
    risks: string;
    learn_more_url: string;
  };
}

export function SystemSecurityCard({ data }: SystemSecurityCardProps) {
  const [selectedAuditor, setSelectedAuditor] = useState<SystemAuditor | null>(null);

  // Extract system auditors (currently just BIOS)
  const systemAuditors: SystemAuditor[] = [];

  if (data['BIOS/UEFI']) {
    systemAuditors.push({
      name: 'BIOS/UEFI',
      ...data['BIOS/UEFI']
    });
  }

  // If no system auditors found, don't render the card
  if (systemAuditors.length === 0) {
    return null;
  }

  // Count risk levels
  const riskCounts = {
    critical: systemAuditors.filter(a => a.risk_level === 'critical').length,
    high: systemAuditors.filter(a => a.risk_level === 'high').length,
    medium: systemAuditors.filter(a => a.risk_level === 'medium').length,
    low: systemAuditors.filter(a => a.risk_level === 'low').length,
    none: systemAuditors.filter(a => a.risk_level === 'none' || !a.installed).length,
  };

  const highestRisk =
    riskCounts.critical > 0 ? 'critical' :
    riskCounts.high > 0 ? 'high' :
    riskCounts.medium > 0 ? 'medium' :
    riskCounts.low > 0 ? 'low' : 'none';

  const borderColor = {
    critical: 'border-red-200 dark:border-red-800',
    high: 'border-orange-200 dark:border-orange-800',
    medium: 'border-yellow-200 dark:border-yellow-800',
    low: 'border-primary-200 dark:border-primary-800',
    none: 'border-gray-200 dark:border-dark-600',
  }[highestRisk];

  return (
    <>
      <div className={`bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border ${borderColor} p-6`}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            System Security
          </h2>
          <span className="text-xs text-gray-500 dark:text-gray-400 px-2 py-1 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
            Beta Preview
          </span>
        </div>

        {/* System Auditors Grid */}
        <div className="space-y-3">
          {systemAuditors.map((auditor) => (
            <SystemAuditorItem
              key={auditor.name}
              auditor={auditor}
              onClick={() => setSelectedAuditor(auditor)}
            />
          ))}
        </div>

        {/* Coming Soon Hint */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-dark-700">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            <span className="font-medium">Coming soon:</span> OS updates, antivirus status, firewall, disk health, backups, encryption, and more.
          </p>
        </div>
      </div>

      {/* Educational Modal */}
      {selectedAuditor && (
        <Modal
          isOpen={!!selectedAuditor}
          onClose={() => setSelectedAuditor(null)}
          title={selectedAuditor.name}
        >
          <div className="space-y-4">
            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
              {selectedAuditor.vendor && (
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Vendor</p>
                  <p className="font-semibold text-gray-900 dark:text-gray-100">{selectedAuditor.vendor}</p>
                </div>
              )}
              {selectedAuditor.version && (
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Version</p>
                  <p className="font-mono text-sm text-gray-900 dark:text-gray-100">{selectedAuditor.version}</p>
                </div>
              )}
              {selectedAuditor.release_date && (
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Release Date</p>
                  <p className="text-sm text-gray-900 dark:text-gray-100">{selectedAuditor.release_date}</p>
                </div>
              )}
              {selectedAuditor.age_days !== undefined && (
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Age</p>
                  <p className="text-sm text-gray-900 dark:text-gray-100">{selectedAuditor.age_days} days old</p>
                </div>
              )}
            </div>

            {/* Risk & Recommendation */}
            {selectedAuditor.recommendation && (
              <div className={`p-4 rounded-lg border ${getRiskColors(selectedAuditor.risk_level).bg} ${getRiskColors(selectedAuditor.risk_level).border}`}>
                <div className="flex items-start gap-2">
                  {getRiskIcon(selectedAuditor.risk_level)}
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 dark:text-gray-100 mb-1">Recommendation</p>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{selectedAuditor.recommendation}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Educational Content */}
            {selectedAuditor.educational_content && (
              <div className="space-y-3">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  Learn More
                </h3>

                <div className="space-y-3 text-sm">
                  <div>
                    <p className="font-medium text-gray-700 dark:text-gray-300 mb-1">What is it?</p>
                    <p className="text-gray-600 dark:text-gray-400">{selectedAuditor.educational_content.what_is_it}</p>
                  </div>

                  <div>
                    <p className="font-medium text-gray-700 dark:text-gray-300 mb-1">Why it matters</p>
                    <p className="text-gray-600 dark:text-gray-400">{selectedAuditor.educational_content.why_it_matters}</p>
                  </div>

                  <div>
                    <p className="font-medium text-gray-700 dark:text-gray-300 mb-1">When to update</p>
                    <p className="text-gray-600 dark:text-gray-400">{selectedAuditor.educational_content.when_to_update}</p>
                  </div>

                  <div>
                    <p className="font-medium text-gray-700 dark:text-gray-300 mb-1">When to skip</p>
                    <p className="text-gray-600 dark:text-gray-400">{selectedAuditor.educational_content.when_to_skip}</p>
                  </div>

                  {selectedAuditor.educational_content.learn_more_url && (
                    <a
                      href={selectedAuditor.educational_content.learn_more_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-primary-600 dark:text-primary-400 hover:underline"
                    >
                      Read full guide →
                    </a>
                  )}
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}
    </>
  );
}

function SystemAuditorItem({ auditor, onClick }: { auditor: SystemAuditor; onClick: () => void }) {
  if (!auditor.installed) {
    return (
      <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-dark-700 rounded-lg border border-gray-200 dark:border-dark-600">
        <div className="flex items-center gap-3">
          <HelpCircle className="w-5 h-5 text-gray-400" />
          <div>
            <p className="font-medium text-gray-500 dark:text-gray-400">{auditor.name}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500">Not available</p>
          </div>
        </div>
      </div>
    );
  }

  const riskColors = getRiskColors(auditor.risk_level);

  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center justify-between p-4 rounded-lg border ${riskColors.bg} ${riskColors.border} hover:shadow-md transition-all`}
    >
      <div className="flex items-center gap-3 text-left">
        {getRiskIcon(auditor.risk_level)}
        <div className="flex-1">
          <p className="font-medium text-gray-900 dark:text-gray-100">{auditor.name}</p>
          {auditor.version && (
            <p className="text-xs text-gray-600 dark:text-gray-400 font-mono mt-0.5">{auditor.version}</p>
          )}
          {auditor.age_days !== undefined && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {auditor.age_days} days old
            </p>
          )}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${riskColors.badge}`}>
          {(auditor.risk_level || 'none').toUpperCase()}
        </span>
        <Info className="w-4 h-4 text-gray-400" />
      </div>
    </button>
  );
}

function getRiskColors(risk_level?: string) {
  const level = risk_level || 'none';

  const colors = {
    critical: {
      bg: 'bg-red-50 dark:bg-red-900/20',
      border: 'border-red-200 dark:border-red-800',
      badge: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800',
    },
    high: {
      bg: 'bg-orange-50 dark:bg-orange-900/20',
      border: 'border-orange-200 dark:border-orange-800',
      badge: 'bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300 border border-orange-200 dark:border-orange-800',
    },
    medium: {
      bg: 'bg-yellow-50 dark:bg-yellow-900/20',
      border: 'border-yellow-200 dark:border-yellow-800',
      badge: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300 border border-yellow-200 dark:border-yellow-800',
    },
    low: {
      bg: 'bg-primary-50 dark:bg-primary-900/20',
      border: 'border-primary-200 dark:border-primary-800',
      badge: 'bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-800',
    },
    none: {
      bg: 'bg-gray-50 dark:bg-dark-700',
      border: 'border-gray-200 dark:border-dark-600',
      badge: 'bg-gray-100 dark:bg-dark-600 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-dark-600',
    },
  };

  return colors[level as keyof typeof colors] || colors.none;
}

function getRiskIcon(risk_level?: string) {
  const level = risk_level || 'none';

  const icons = {
    critical: <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />,
    high: <AlertTriangle className="w-5 h-5 text-orange-600 dark:text-orange-400" />,
    medium: <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />,
    low: <CheckCircle className="w-5 h-5 text-primary-600 dark:text-primary-400" />,
    none: <Shield className="w-5 h-5 text-gray-400" />,
  };

  return icons[level as keyof typeof icons] || icons.none;
}
