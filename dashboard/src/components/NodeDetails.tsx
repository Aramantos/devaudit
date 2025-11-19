import { Box, AlertTriangle } from 'lucide-react';
import { ActionablePackageList } from './ActionablePackageList';

interface NodeDetailsProps {
  data: any;
}

async function upgradeNodePackages(packages: string[]) {
  const response = await fetch('/api/cleanup/node/upgrade', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(packages),
  });

  if (!response.ok) {
    throw new Error('Failed to upgrade packages');
  }

  return response.json();
}

export function NodeDetails({ data }: NodeDetailsProps) {
  if (!data?.installed) {
    return (
      <div className="bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border border-gray-200 dark:border-dark-700 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <Box className="w-5 h-5" />
          Node.js
        </h2>
        <p className="text-gray-500 dark:text-gray-400">Not installed</p>
      </div>
    );
  }

  const globalPackages = data.global_packages?.length || 0;
  const outdatedCount = data.outdated_packages?.length || 0;
  const hasPackageJson = data.has_package_json;

  return (
    <div className="bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border border-gray-200 dark:border-dark-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <Box className="w-5 h-5 text-green-600 dark:text-green-400" />
          Node.js
        </h2>
        <span className="text-sm text-gray-500 dark:text-gray-400">{data.node_version}</span>
      </div>

      <div className="space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-50 dark:bg-dark-700 border border-gray-100 dark:border-dark-600 rounded p-3">
            <p className="text-sm text-gray-600 dark:text-gray-400">Global Packages</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{globalPackages}</p>
          </div>
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-100 dark:border-yellow-800 rounded p-3">
            <p className="text-sm text-gray-600 dark:text-gray-400">Outdated</p>
            <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{outdatedCount}</p>
          </div>
        </div>

        {/* Project Info */}
        {hasPackageJson && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded p-3">
            <p className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-1">Project Detected</p>
            <div className="text-xs text-blue-700 dark:text-blue-400 space-y-1">
              {data.dependencies && (
                <p>{Object.keys(data.dependencies).length} dependencies</p>
              )}
              {data.dev_dependencies && (
                <p>{Object.keys(data.dev_dependencies).length} dev dependencies</p>
              )}
              {data.node_modules_count && (
                <p>{data.node_modules_count} packages in node_modules</p>
              )}
            </div>
          </div>
        )}

        {/* Outdated Packages */}
        {outdatedCount > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
              Outdated Packages - Interactive Upgrade
            </h3>
            <ActionablePackageList
              packages={data.outdated_packages}
              tool="Node.js"
              onUpgrade={upgradeNodePackages}
            />
          </div>
        )}

        {/* Frameworks */}
        {data.frameworks && Object.keys(data.frameworks).length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Frameworks</h3>
            <div className="flex flex-wrap gap-2">
              {Object.entries(data.frameworks).map(([framework, detected]: [string, any]) => (
                detected && (
                  <span key={framework} className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-800 text-xs rounded">
                    {framework}
                  </span>
                )
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
