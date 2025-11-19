import { useState, useMemo } from 'react';
import { Search, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';

interface Package {
  name: string;
  version?: string;
  current?: string;
  latest?: string;
  source?: string;
  location?: string;
}

interface PackageTableProps {
  packages: Package[];
  showLatest?: boolean;
  showSource?: boolean;
}

type SortKey = 'name' | 'version' | 'current' | 'latest';
type SortDirection = 'asc' | 'desc';

export function PackageTable({ packages, showLatest = false, showSource = false }: PackageTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortKey, setSortKey] = useState<SortKey>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const filteredAndSortedPackages = useMemo(() => {
    let result = packages.filter(pkg =>
      pkg.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    result.sort((a, b) => {
      const aVal = a[sortKey] || '';
      const bVal = b[sortKey] || '';

      const comparison = aVal.toString().localeCompare(bVal.toString(), undefined, { numeric: true });
      return sortDirection === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [packages, searchTerm, sortKey, sortDirection]);

  const SortIcon = ({ column }: { column: SortKey }) => {
    if (sortKey !== column) {
      return <ArrowUpDown className="w-4 h-4 text-gray-400 dark:text-gray-500" />;
    }
    return sortDirection === 'asc' ? (
      <ArrowUp className="w-4 h-4 text-primary-500 dark:text-primary-400" />
    ) : (
      <ArrowDown className="w-4 h-4 text-primary-500 dark:text-primary-400" />
    );
  };

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
        <input
          type="text"
          placeholder="Search packages..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
        />
      </div>

      {/* Package Count */}
      <div className="text-sm text-gray-600 dark:text-gray-400">
        Showing {filteredAndSortedPackages.length} of {packages.length} packages
      </div>

      {/* Table */}
      <div className="overflow-x-auto border border-gray-200 dark:border-dark-700 rounded-lg">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-dark-700 border-b border-gray-200 dark:border-dark-600">
            <tr>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('name')}
                  className="flex items-center gap-2 font-semibold text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                >
                  Package Name
                  <SortIcon column="name" />
                </button>
              </th>
              {!showLatest ? (
                <th className="px-4 py-3 text-left">
                  <button
                    onClick={() => handleSort('version')}
                    className="flex items-center gap-2 font-semibold text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                  >
                    Version
                    <SortIcon column="version" />
                  </button>
                </th>
              ) : (
                <>
                  <th className="px-4 py-3 text-left">
                    <button
                      onClick={() => handleSort('current')}
                      className="flex items-center gap-2 font-semibold text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                    >
                      Current
                      <SortIcon column="current" />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left">
                    <button
                      onClick={() => handleSort('latest')}
                      className="flex items-center gap-2 font-semibold text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                    >
                      Latest
                      <SortIcon column="latest" />
                    </button>
                  </th>
                </>
              )}
              {showSource && (
                <th className="px-4 py-3 text-left">
                  <span className="font-semibold text-gray-700 dark:text-gray-300">
                    Source
                  </span>
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-dark-600">
            {filteredAndSortedPackages.length === 0 ? (
              <tr>
                <td
                  colSpan={showLatest ? (showSource ? 4 : 3) : (showSource ? 3 : 2)}
                  className="px-4 py-8 text-center text-gray-500 dark:text-gray-400"
                >
                  No packages found
                </td>
              </tr>
            ) : (
              filteredAndSortedPackages.map((pkg, idx) => (
                <tr
                  key={idx}
                  className="bg-white dark:bg-dark-800 hover:bg-gray-50 dark:hover:bg-dark-750 transition-colors"
                >
                  <td className="px-4 py-3 font-medium text-gray-900 dark:text-gray-100">
                    {pkg.name}
                  </td>
                  {!showLatest ? (
                    <td className="px-4 py-3 text-gray-600 dark:text-gray-400 font-mono text-sm">
                      {pkg.version}
                    </td>
                  ) : (
                    <>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-400 font-mono text-sm">
                        {pkg.current}
                      </td>
                      <td className="px-4 py-3 text-primary-600 dark:text-primary-400 font-mono text-sm font-semibold">
                        {pkg.latest}
                      </td>
                    </>
                  )}
                  {showSource && (
                    <td className="px-4 py-3 text-gray-500 dark:text-gray-400 text-sm">
                      {pkg.source}
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
