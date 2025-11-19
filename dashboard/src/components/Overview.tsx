import { useState } from 'react';
import { Package, AlertTriangle, CheckCircle, Layers, Info } from 'lucide-react';
import { Modal } from './Modal';
import { PackageTable } from './PackageTable';

interface OverviewProps {
  data: any;
}

export function Overview({ data }: OverviewProps) {
  const [activeModal, setActiveModal] = useState<string | null>(null);

  const tools = Object.keys(data);
  const installed = tools.filter(tool => data[tool]?.installed).length;
  const totalOutdated = countOutdated(data);
  const totalCleanup = countCleanupCandidates(data);
  const totalPackages = countTotalPackages(data);

  // Aggregate all packages from all tools
  const allPackages = getAllPackages(data);
  const outdatedPackages = getOutdatedPackages(data);
  const cleanupBreakdown = getCleanupBreakdown(data);

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Tools Detected"
          value={installed}
          subtitle={`of ${tools.length} total`}
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
          onClick={() => setActiveModal('tools')}
          clickable
        />
        <StatCard
          title="Total Packages"
          value={totalPackages}
          icon={<Package className="w-6 h-6" />}
          color="electric"
          onClick={() => setActiveModal('packages')}
          clickable
        />
        <StatCard
          title="Outdated Packages"
          value={totalOutdated}
          icon={<AlertTriangle className="w-6 h-6" />}
          color="yellow"
          onClick={() => setActiveModal('outdated')}
          clickable
        />
        <StatCard
          title="Cleanup Items"
          value={totalCleanup}
          icon={<Layers className="w-6 h-6" />}
          color="orange"
          onClick={() => setActiveModal('cleanup')}
          clickable
          tooltip="Includes outdated packages, security vulnerabilities, and Docker cleanup candidates (stopped containers, unused images)"
        />
      </div>

      {/* Tools Detected Modal */}
      <Modal
        isOpen={activeModal === 'tools'}
        onClose={() => setActiveModal(null)}
        title="Detected Tools"
      >
        <div className="space-y-3">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Development tools and package managers found on your system
          </p>
          {Object.entries(data).map(([toolName, toolData]: [string, any]) => (
            <div
              key={toolName}
              className={`p-4 rounded-lg border ${
                toolData?.installed
                  ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800'
                  : 'bg-gray-50 dark:bg-dark-700 border-gray-200 dark:border-dark-600'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                    {toolName}
                  </h3>
                  {toolData?.version && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 font-mono mt-1">
                      Version: {toolData.version}
                    </p>
                  )}
                  {toolData?.location && (
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-1 truncate max-w-md">
                      {toolData.location}
                    </p>
                  )}
                </div>
                <div>
                  {toolData?.installed ? (
                    <CheckCircle className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                  ) : (
                    <div className="text-xs text-gray-400 dark:text-gray-500">Not found</div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Modal>

      {/* All Packages Modal */}
      <Modal
        isOpen={activeModal === 'packages'}
        onClose={() => setActiveModal(null)}
        title="All Packages"
      >
        <PackageTable packages={allPackages} showSource />
      </Modal>

      {/* Outdated Packages Modal */}
      <Modal
        isOpen={activeModal === 'outdated'}
        onClose={() => setActiveModal(null)}
        title="Outdated Packages"
      >
        <PackageTable packages={outdatedPackages} showLatest showSource />
      </Modal>

      {/* Cleanup Items Modal */}
      <Modal
        isOpen={activeModal === 'cleanup'}
        onClose={() => setActiveModal(null)}
        title="Cleanup Items Breakdown"
      >
        <div className="space-y-6">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Cleanup items are issues or optimizations that need attention in your development environment.
          </p>

          {/* Outdated Packages */}
          {cleanupBreakdown.outdated.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                  Outdated Packages ({cleanupBreakdown.outdated.length})
                </h3>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 ml-6">
                Packages with newer versions available
              </p>
              <div className="ml-6 space-y-1">
                {cleanupBreakdown.outdated.slice(0, 10).map((item: any, idx: number) => (
                  <div key={idx} className="text-sm text-gray-700 dark:text-gray-300 font-mono bg-gray-50 dark:bg-dark-700 px-3 py-2 rounded border border-gray-200 dark:border-dark-600">
                    <span className="font-semibold">{item.name}</span>
                    <span className="text-gray-500 dark:text-gray-400 mx-2">→</span>
                    <span className="text-yellow-600 dark:text-yellow-400">{item.current}</span>
                    <span className="text-gray-500 dark:text-gray-400 mx-2">to</span>
                    <span className="text-primary-600 dark:text-primary-400">{item.latest}</span>
                    <span className="text-gray-500 dark:text-gray-400 text-xs ml-2">({item.source})</span>
                  </div>
                ))}
                {cleanupBreakdown.outdated.length > 10 && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 pt-2">
                    +{cleanupBreakdown.outdated.length - 10} more
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Security Vulnerabilities */}
          {cleanupBreakdown.vulnerabilities.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-600 dark:text-red-400" />
                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                  Security Vulnerabilities ({cleanupBreakdown.vulnerabilities.length})
                </h3>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 ml-6">
                Known security issues in installed packages
              </p>
              <div className="ml-6 space-y-1">
                {cleanupBreakdown.vulnerabilities.slice(0, 10).map((item: any, idx: number) => (
                  <div key={idx} className="text-sm text-gray-700 dark:text-gray-300 font-mono bg-red-50 dark:bg-red-900/20 px-3 py-2 rounded border border-red-200 dark:border-red-800">
                    <span className="font-semibold text-red-700 dark:text-red-300">{item.package}</span>
                    <span className="text-gray-500 dark:text-gray-400 mx-2">•</span>
                    <span className="text-xs">{item.id || item.title}</span>
                  </div>
                ))}
                {cleanupBreakdown.vulnerabilities.length > 10 && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 pt-2">
                    +{cleanupBreakdown.vulnerabilities.length - 10} more
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Docker Cleanup */}
          {cleanupBreakdown.docker.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-orange-600 dark:text-orange-400" />
                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                  Docker Cleanup ({cleanupBreakdown.docker.length})
                </h3>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 ml-6">
                Stopped containers, unused images, and dangling volumes
              </p>
              <div className="ml-6 space-y-1">
                {cleanupBreakdown.docker.slice(0, 10).map((item: any, idx: number) => (
                  <div key={idx} className="text-sm text-gray-700 dark:text-gray-300 font-mono bg-orange-50 dark:bg-orange-900/20 px-3 py-2 rounded border border-orange-200 dark:border-orange-800">
                    <span className="text-xs text-gray-500 dark:text-gray-400">{item.type}:</span>
                    <span className="ml-2">{item.name || item.id}</span>
                  </div>
                ))}
                {cleanupBreakdown.docker.length > 10 && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 pt-2">
                    +{cleanupBreakdown.docker.length - 10} more
                  </p>
                )}
              </div>
            </div>
          )}

          {totalCleanup === 0 && (
            <div className="text-center py-8">
              <CheckCircle className="w-12 h-12 text-primary-600 dark:text-primary-400 mx-auto mb-3" />
              <p className="text-gray-600 dark:text-gray-400">
                All clear! No cleanup items detected.
              </p>
            </div>
          )}
        </div>
      </Modal>
    </>
  );
}

interface StatCardProps {
  title: string;
  value: number;
  subtitle?: string;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'yellow' | 'orange' | 'electric';
  onClick?: () => void;
  clickable?: boolean;
  tooltip?: string;
}

function StatCard({ title, value, subtitle, icon, color, onClick, clickable, tooltip }: StatCardProps) {
  const colorClasses = {
    blue: {
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      text: 'text-blue-600 dark:text-blue-400',
      border: 'border-blue-200 dark:border-blue-800'
    },
    electric: {
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      text: 'text-blue-600 dark:text-blue-400',
      border: 'border-blue-200 dark:border-blue-800'
    },
    green: {
      bg: 'bg-primary-50 dark:bg-primary-900/20',
      text: 'text-primary-600 dark:text-primary-400',
      border: 'border-primary-200 dark:border-primary-800'
    },
    yellow: {
      bg: 'bg-yellow-50 dark:bg-yellow-900/20',
      text: 'text-yellow-600 dark:text-yellow-400',
      border: 'border-yellow-200 dark:border-yellow-800'
    },
    orange: {
      bg: 'bg-orange-50 dark:bg-orange-900/20',
      text: 'text-orange-600 dark:text-orange-400',
      border: 'border-orange-200 dark:border-orange-800'
    },
  };

  const colors = colorClasses[color];

  const Component = clickable ? 'button' : 'div';

  return (
    <Component
      onClick={onClick}
      className={`bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border ${colors.border} p-6 hover:shadow-md dark:hover:shadow-primary-500/10 transition-all ${clickable ? 'cursor-pointer hover:scale-105 active:scale-100' : ''} w-full text-left`}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-1.5">
            <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">{title}</p>
            {tooltip && (
              <div className="group relative">
                <Info className="w-3.5 h-3.5 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 cursor-help" />
                <div className="absolute left-0 top-6 w-64 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs rounded-lg p-3 shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 pointer-events-none">
                  {tooltip}
                  <div className="absolute -top-1 left-4 w-2 h-2 bg-gray-900 dark:bg-gray-100 transform rotate-45"></div>
                </div>
              </div>
            )}
          </div>
          <p className="text-3xl font-bold mt-2 text-gray-900 dark:text-gray-100">
            {value}
          </p>
          {subtitle && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 rounded-full ${colors.bg} ${colors.text}`}>
          {icon}
        </div>
      </div>
    </Component>
  );
}

function countOutdated(data: any): number {
  return Object.values(data).reduce((sum: number, tool: any) => {
    return sum + (tool?.outdated_packages?.length || 0);
  }, 0);
}

function countCleanupCandidates(data: any): number {
  let count = 0;

  Object.values(data).forEach((tool: any) => {
    const candidates = tool?.cleanup_candidates || [];

    if (candidates.length > 0) {
      // If tool has cleanup_candidates, sum up their counts
      candidates.forEach((candidate: any) => {
        count += candidate?.count || 1; // Use count field if available, otherwise count the candidate itself
      });
    } else {
      // Fallback: if no cleanup_candidates, count outdated + vulnerabilities directly
      count += tool?.outdated_packages?.length || 0;
      count += tool?.vulnerabilities?.length || 0;
    }
  });

  return count;
}

function countTotalPackages(data: any): number {
  return Object.values(data).reduce((sum: number, tool: any) => {
    return sum + (tool?.packages?.length || 0);
  }, 0);
}

function getAllPackages(data: any): any[] {
  const packages: any[] = [];

  Object.entries(data).forEach(([toolName, toolData]: [string, any]) => {
    if (toolData?.packages) {
      toolData.packages.forEach((pkg: any) => {
        packages.push({
          name: pkg.name || pkg,
          version: pkg.version || pkg.current,
          source: toolName,
        });
      });
    }

    // Also include global packages from Node
    if (toolData?.global_packages) {
      toolData.global_packages.forEach((pkg: any) => {
        packages.push({
          name: pkg.name || pkg,
          version: pkg.version,
          source: `${toolName} (global)`,
        });
      });
    }
  });

  return packages;
}

function getOutdatedPackages(data: any): any[] {
  const packages: any[] = [];

  Object.entries(data).forEach(([toolName, toolData]: [string, any]) => {
    if (toolData?.outdated_packages) {
      toolData.outdated_packages.forEach((pkg: any) => {
        packages.push({
          name: pkg.name,
          current: pkg.current,
          latest: pkg.latest,
          source: toolName,
        });
      });
    }
  });

  return packages;
}

function getCleanupBreakdown(data: any): { outdated: any[], vulnerabilities: any[], docker: any[] } {
  const breakdown = {
    outdated: [] as any[],
    vulnerabilities: [] as any[],
    docker: [] as any[],
  };

  Object.entries(data).forEach(([toolName, toolData]: [string, any]) => {
    // Collect outdated packages
    if (toolData?.outdated_packages) {
      toolData.outdated_packages.forEach((pkg: any) => {
        breakdown.outdated.push({
          name: pkg.name,
          current: pkg.current,
          latest: pkg.latest,
          source: toolName,
        });
      });
    }

    // Collect vulnerabilities
    if (toolData?.vulnerabilities) {
      toolData.vulnerabilities.forEach((vuln: any) => {
        breakdown.vulnerabilities.push({
          package: vuln.package,
          id: vuln.id || vuln.cve_id,
          title: vuln.title,
          severity: vuln.severity,
          source: toolName,
        });
      });
    }

    // Collect Docker cleanup candidates
    if (toolName === 'Docker' && toolData?.cleanup_candidates) {
      toolData.cleanup_candidates.forEach((item: any) => {
        breakdown.docker.push({
          type: item.type || 'container',
          name: item.name,
          id: item.id,
        });
      });
    }
  });

  return breakdown;
}
