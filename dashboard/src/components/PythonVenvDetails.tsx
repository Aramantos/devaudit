'use client';

import { useState } from 'react';
import { Package, FolderTree, AlertTriangle, CheckCircle, ChevronDown, ChevronUp, Trash2 } from 'lucide-react';
import { ConfirmModal } from './ConfirmModal';

interface PythonVenvDetailsProps {
  data: any;
}

async function uninstallGlobalPackages(packages: string[]) {
  const response = await fetch('/api/cleanup/python/uninstall', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(packages),
  });

  if (!response.ok) {
    throw new Error('Failed to uninstall packages');
  }

  return response.json();
}

export function PythonVenvDetails({ data }: PythonVenvDetailsProps) {
  const [selectedEnv, setSelectedEnv] = useState<string | null>(null);
  const [showDuplicates, setShowDuplicates] = useState(false);
  const [showOrphaned, setShowOrphaned] = useState(false);
  const [selectedOrphaned, setSelectedOrphaned] = useState<Set<string>>(new Set());
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [isUninstalling, setIsUninstalling] = useState(false);

  if (!data?.installed) {
    return null;
  }

  const environments = data.environments || [];
  const duplicates = data.duplicate_packages || [];
  const orphaned = data.orphaned_global || [];
  const recommendations = data.recommendations || [];

  // Select first environment by default
  if (!selectedEnv && environments.length > 0) {
    setSelectedEnv(environments[0].name);
  }

  const currentEnv = environments.find((env: any) => env.name === selectedEnv);

  const toggleOrphanedSelection = (pkg: string) => {
    const newSet = new Set(selectedOrphaned);
    if (newSet.has(pkg)) {
      newSet.delete(pkg);
    } else {
      newSet.add(pkg);
    }
    setSelectedOrphaned(newSet);
  };

  const toggleSelectAllOrphaned = () => {
    if (selectedOrphaned.size === orphaned.length) {
      setSelectedOrphaned(new Set());
    } else {
      setSelectedOrphaned(new Set(orphaned));
    }
  };

  const openDeleteModal = () => {
    if (selectedOrphaned.size > 0) {
      setDeleteModalOpen(true);
    }
  };

  const confirmDelete = async () => {
    setIsUninstalling(true);
    try {
      const packagesToUninstall = Array.from(selectedOrphaned);
      await uninstallGlobalPackages(packagesToUninstall);
      // Refresh the page to show updated data
      window.location.reload();
    } catch (error) {
      console.error('Failed to uninstall packages:', error);
      alert('Failed to uninstall some packages. Check console for details.');
    } finally {
      setIsUninstalling(false);
      setDeleteModalOpen(false);
      setSelectedOrphaned(new Set());
    }
  };

  const cancelDelete = () => {
    setDeleteModalOpen(false);
  };

  return (
    <div className="bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border border-gray-200 dark:border-dark-700 p-6">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
        <FolderTree className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        Python Environments
      </h2>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div className="p-3 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
          <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Environments</p>
          <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">{environments.length}</p>
        </div>
        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Total Packages</p>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{data.total_packages || 0}</p>
        </div>
        <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
          <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Duplicates</p>
          <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{duplicates.length}</p>
        </div>
        <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
          <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Orphaned Global</p>
          <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">{orphaned.length}</p>
        </div>
      </div>

      {/* Environment Selector */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Select Environment:
        </label>
        <select
          value={selectedEnv || ''}
          onChange={(e) => setSelectedEnv(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 dark:border-dark-600 rounded-lg bg-white dark:bg-dark-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
        >
          {environments.map((env: any) => (
            <option key={env.name} value={env.name}>
              {env.name} ({env.package_count || 0} packages)
            </option>
          ))}
        </select>
      </div>

      {/* Current Environment Details */}
      {currentEnv && (
        <div className="mb-6 p-4 bg-gray-50 dark:bg-dark-700 rounded-lg border border-gray-200 dark:border-dark-600">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Type</p>
              <p className="font-semibold text-gray-900 dark:text-gray-100 capitalize">{currentEnv.type}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Python Version</p>
              <p className="font-mono text-sm text-gray-900 dark:text-gray-100">{currentEnv.python_version || 'Unknown'}</p>
            </div>
            <div className="md:col-span-2">
              <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Path</p>
              <p className="font-mono text-xs text-gray-700 dark:text-gray-300 break-all">{currentEnv.path || 'N/A'}</p>
            </div>
            {currentEnv.has_requirements !== undefined && (
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Requirements.txt</p>
                <p className="flex items-center gap-2">
                  {currentEnv.has_requirements ? (
                    <>
                      <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
                      <span className="text-sm text-green-600 dark:text-green-400">
                        Present ({currentEnv.requirements_packages?.length || 0} packages)
                      </span>
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-4 h-4 text-orange-600 dark:text-orange-400" />
                      <span className="text-sm text-orange-600 dark:text-orange-400">Missing</span>
                    </>
                  )}
                </p>
              </div>
            )}
          </div>

          {/* Packages List */}
          <div className="mt-4">
            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Packages ({currentEnv.packages?.length || 0}):
            </p>
            <div className="max-h-60 overflow-y-auto bg-white dark:bg-dark-800 rounded border border-gray-200 dark:border-dark-600 p-3">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {currentEnv.packages?.map((pkg: any, idx: number) => (
                  <div key={idx} className="text-xs font-mono text-gray-700 dark:text-gray-300 flex items-center gap-1">
                    <Package className="w-3 h-3 text-primary-500 flex-shrink-0" />
                    <span className="truncate">{pkg.name}</span>
                    <span className="text-gray-400 dark:text-gray-500">{pkg.version}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Duplicate Packages Section */}
      {duplicates.length > 0 && (
        <div className="mb-4">
          <button
            onClick={() => setShowDuplicates(!showDuplicates)}
            className="flex items-center justify-between w-full p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800 hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-colors"
          >
            <span className="flex items-center gap-2 text-sm font-semibold text-yellow-700 dark:text-yellow-300">
              <AlertTriangle className="w-4 h-4" />
              Duplicate Packages ({duplicates.length})
            </span>
            {showDuplicates ? (
              <ChevronUp className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
            )}
          </button>

          {showDuplicates && (
            <div className="mt-2 p-4 bg-white dark:bg-dark-700 rounded-lg border border-gray-200 dark:border-dark-600 max-h-60 overflow-y-auto">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                These packages exist in multiple environments. Consider removing duplicates to save space.
              </p>
              {duplicates.slice(0, 15).map((dup: any, idx: number) => (
                <div key={idx} className="mb-3 pb-3 border-b border-gray-100 dark:border-dark-600 last:border-0">
                  <p className="font-mono text-sm font-semibold text-gray-900 dark:text-gray-100">{dup.name}</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    Found in {dup.count} environments: {dup.environments.slice(0, 3).join(', ')}
                    {dup.environments.length > 3 && ` +${dup.environments.length - 3} more`}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Orphaned Global Packages Section */}
      {orphaned.length > 0 && (
        <div className="mb-4">
          <button
            onClick={() => setShowOrphaned(!showOrphaned)}
            className="flex items-center justify-between w-full p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800 hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors"
          >
            <span className="flex items-center gap-2 text-sm font-semibold text-orange-700 dark:text-orange-300">
              <AlertTriangle className="w-4 h-4" />
              Orphaned Global Packages ({orphaned.length})
            </span>
            {showOrphaned ? (
              <ChevronUp className="w-4 h-4 text-orange-600 dark:text-orange-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-orange-600 dark:text-orange-400" />
            )}
          </button>

          {showOrphaned && (
            <div className="mt-2 p-4 bg-white dark:bg-dark-700 rounded-lg border border-gray-200 dark:border-dark-600">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                These global packages are also installed in project venvs. Removing them from global helps avoid conflicts.
              </p>

              {/* Select All and Delete Actions */}
              <div className="flex items-center justify-between mb-3 pb-3 border-b border-gray-200 dark:border-dark-600">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedOrphaned.size === orphaned.length && orphaned.length > 0}
                    onChange={toggleSelectAllOrphaned}
                    className="w-4 h-4 text-orange-600 bg-gray-100 border-gray-300 rounded focus:ring-orange-500 dark:focus:ring-orange-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                  />
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                    Select All ({selectedOrphaned.size}/{orphaned.length})
                  </span>
                </label>

                <button
                  onClick={openDeleteModal}
                  disabled={selectedOrphaned.size === 0}
                  className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-red-600 hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-lg transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Uninstall Selected
                </button>
              </div>

              {/* Package List with Checkboxes */}
              <div className="max-h-60 overflow-y-auto space-y-2">
                {orphaned.map((pkg: string, idx: number) => (
                  <label key={idx} className="flex items-center gap-2 p-2 hover:bg-gray-50 dark:hover:bg-dark-600 rounded cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedOrphaned.has(pkg)}
                      onChange={() => toggleOrphanedSelection(pkg)}
                      className="w-4 h-4 text-orange-600 bg-gray-100 border-gray-300 rounded focus:ring-orange-500 dark:focus:ring-orange-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                    />
                    <Package className="w-3.5 h-3.5 text-orange-500 flex-shrink-0" />
                    <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{pkg}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <p className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-2">Recommendations:</p>
          <ul className="space-y-2">
            {recommendations.map((rec: string, idx: number) => (
              <li key={idx} className="text-sm text-blue-800 dark:text-blue-200 flex items-start gap-2">
                <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Delete Confirmation Modal with Humble Warning */}
      <ConfirmModal
        isOpen={deleteModalOpen}
        title="Uninstall Global Packages?"
        message={`You are about to uninstall ${selectedOrphaned.size} global package${selectedOrphaned.size !== 1 ? 's' : ''}. While our detection system identifies these as orphaned (also installed in your project venvs), we want to be transparent: our system is not foolproof. This action could potentially cause issues we cannot foresee, especially if other non-Python applications depend on these global packages. Are you sure you want to proceed?`}
        confirmText={isUninstalling ? "Uninstalling..." : "Yes, Uninstall"}
        cancelText="Cancel"
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
        variant="danger"
      />
    </div>
  );
}
