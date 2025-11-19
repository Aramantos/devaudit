import { useState } from 'react';
import { Check, Loader, AlertCircle, CheckCircle2 } from 'lucide-react';

interface Package {
  name: string;
  current: string;
  latest: string;
}

interface ActionablePackageListProps {
  packages: Package[];
  tool: string;
  onUpgrade: (packages: string[]) => Promise<void>;
}

export function ActionablePackageList({ packages, tool, onUpgrade }: ActionablePackageListProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [upgrading, setUpgrading] = useState(false);
  const [results, setResults] = useState<Map<string, { success: boolean; message: string }>>(
    new Map()
  );

  const togglePackage = (packageName: string) => {
    const newSelected = new Set(selected);
    if (newSelected.has(packageName)) {
      newSelected.delete(packageName);
    } else {
      newSelected.add(packageName);
    }
    setSelected(newSelected);
  };

  const selectAll = () => {
    setSelected(new Set(packages.map(p => p.name)));
  };

  const deselectAll = () => {
    setSelected(new Set());
  };

  const handleUpgrade = async () => {
    if (selected.size === 0) return;

    setUpgrading(true);
    setResults(new Map());

    try {
      await onUpgrade(Array.from(selected));

      // Mark all as successful (you can enhance this to show individual results)
      const newResults = new Map<string, { success: boolean; message: string }>();
      selected.forEach(pkg => {
        newResults.set(pkg, { success: true, message: 'Upgraded successfully' });
      });
      setResults(newResults);

      // Clear selection after successful upgrade
      setTimeout(() => {
        setSelected(new Set());
        setResults(new Map());
      }, 3000);
    } catch (error) {
      // Show error
      const newResults = new Map<string, { success: boolean; message: string }>();
      selected.forEach(pkg => {
        newResults.set(pkg, { success: false, message: 'Upgrade failed' });
      });
      setResults(newResults);
    } finally {
      setUpgrading(false);
    }
  };

  if (packages.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      {/* Action Bar */}
      <div className="flex items-center justify-between gap-4 pb-3 border-b border-gray-200 dark:border-dark-600">
        <div className="flex items-center gap-2">
          <button
            onClick={selectAll}
            className="text-xs text-primary-600 dark:text-primary-400 hover:underline"
          >
            Select All
          </button>
          <span className="text-gray-300 dark:text-gray-600">|</span>
          <button
            onClick={deselectAll}
            className="text-xs text-gray-600 dark:text-gray-400 hover:underline"
          >
            Deselect All
          </button>
          {selected.size > 0 && (
            <span className="text-xs text-gray-600 dark:text-gray-400 ml-2">
              ({selected.size} selected)
            </span>
          )}
        </div>

        <button
          onClick={handleUpgrade}
          disabled={selected.size === 0 || upgrading}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 text-white rounded-lg text-sm font-semibold transition-colors disabled:cursor-not-allowed flex items-center gap-2"
        >
          {upgrading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Upgrading...
            </>
          ) : (
            <>
              Upgrade Selected ({selected.size})
            </>
          )}
        </button>
      </div>

      {/* Package List */}
      <div className="space-y-2">
        {packages.map((pkg) => {
          const isSelected = selected.has(pkg.name);
          const result = results.get(pkg.name);

          return (
            <div
              key={pkg.name}
              className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${
                isSelected
                  ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-300 dark:border-primary-700'
                  : 'bg-gray-50 dark:bg-dark-700 border-gray-200 dark:border-dark-600 hover:border-gray-300 dark:hover:border-dark-500'
              }`}
            >
              {/* Checkbox */}
              <button
                onClick={() => togglePackage(pkg.name)}
                className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                  isSelected
                    ? 'bg-primary-600 border-primary-600 dark:bg-primary-500 dark:border-primary-500'
                    : 'border-gray-300 dark:border-gray-600 hover:border-primary-500'
                }`}
              >
                {isSelected && <Check className="w-3.5 h-3.5 text-white" />}
              </button>

              {/* Package Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900 dark:text-gray-100">{pkg.name}</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                    {pkg.current} → <span className="text-primary-600 dark:text-primary-400 font-semibold">{pkg.latest}</span>
                  </span>
                </div>

                {/* Result Message */}
                {result && (
                  <div className={`text-xs mt-1 flex items-center gap-1 ${
                    result.success
                      ? 'text-green-600 dark:text-green-400'
                      : 'text-red-600 dark:text-red-400'
                  }`}>
                    {result.success ? (
                      <CheckCircle2 className="w-3.5 h-3.5" />
                    ) : (
                      <AlertCircle className="w-3.5 h-3.5" />
                    )}
                    {result.message}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
