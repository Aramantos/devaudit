import { AlertTriangle, Package, CheckCircle } from 'lucide-react';
import { ActionablePackageList } from './ActionablePackageList';

interface PythonDetailsProps {
  data: any;
}

async function upgradePythonPackages(packages: string[]) {
  const response = await fetch('/api/cleanup/python/upgrade', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(packages),
  });

  if (!response.ok) {
    throw new Error('Failed to upgrade packages');
  }

  return response.json();
}

export function PythonDetails({ data }: PythonDetailsProps) {
  if (!data?.installed) {
    return (
      <div className="bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 p-6 border border-gray-200 dark:border-dark-700">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-gray-900 dark:text-gray-100">
          <Package className="w-5 h-5 text-gray-400 dark:text-gray-500" />
          Python
        </h2>
        <p className="text-gray-500 dark:text-gray-400">Not installed</p>
      </div>
    );
  }

  const totalPackages = data.packages?.length || 0;
  const outdatedCount = data.outdated_packages?.length || 0;

  return (
    <div className="bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 p-6 border border-gray-200 dark:border-dark-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold flex items-center gap-2 text-gray-900 dark:text-gray-100">
          <Package className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          Python
        </h2>
        <span className="text-sm text-gray-500 dark:text-gray-400">{data.version}</span>
      </div>

      <div className="space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-50 dark:bg-dark-700 rounded p-3 border border-gray-100 dark:border-dark-600">
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Packages</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{totalPackages}</p>
          </div>
          <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded p-3 border border-yellow-100 dark:border-yellow-800">
            <p className="text-sm text-gray-600 dark:text-gray-400">Outdated</p>
            <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{outdatedCount}</p>
          </div>
        </div>

        {/* Outdated Packages */}
        {outdatedCount > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
              Outdated Packages - Interactive Upgrade
            </h3>
            <ActionablePackageList
              packages={data.outdated_packages}
              tool="Python"
              onUpgrade={upgradePythonPackages}
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
                  <span key={framework} className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-xs rounded border border-primary-200 dark:border-primary-800">
                    {framework}
                  </span>
                )
              ))}
            </div>
          </div>
        )}

        {/* Package Health Summary - fills empty space */}
        {outdatedCount === 0 && (
          <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
              <h3 className="text-sm font-semibold text-green-900 dark:text-green-100">
                All Packages Up to Date
              </h3>
            </div>
            <p className="text-xs text-green-700 dark:text-green-300">
              All {totalPackages} installed packages are running the latest available versions.
              Great job keeping your Python environment secure and up-to-date!
            </p>
          </div>
        )}

        {/* Quick Actions - always visible */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-dark-600">
          <h3 className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">Quick Actions</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => navigator.clipboard.writeText('pip list --outdated')}
              className="px-3 py-1.5 text-xs bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 text-gray-700 dark:text-gray-300 rounded transition-colors"
            >
              Copy Check Command
            </button>
            <button
              onClick={() => navigator.clipboard.writeText('pip freeze > requirements.txt')}
              className="px-3 py-1.5 text-xs bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 text-gray-700 dark:text-gray-300 rounded transition-colors"
            >
              Copy Freeze Command
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
