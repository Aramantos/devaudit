import { useState, useEffect, useRef } from 'react';
import { Clock, TrendingDown, TrendingUp, Calendar, ChevronRight, Trash2, GitCompare, Download, FileJson, FileText, Search, X, Edit2, Save, Tag, Command } from 'lucide-react';
import { useKeyboardShortcuts } from '@/lib/useKeyboardShortcuts';
import { ConfirmModal } from './ConfirmModal';

interface HistoryScan {
  id: string;
  timestamp: string;
  metadata?: {
    notes?: string;
  };
  summary: {
    total_packages: number;
    outdated_packages: number;
    vulnerabilities: number;
    cleanup_items: number;
    tools_detected: number;
  };
}

interface ScanHistoryProps {
  currentScanId?: string;
  onCompare?: (scanId1: string, scanId2: string) => void;
}

export function ScanHistory({ currentScanId, onCompare }: ScanHistoryProps) {
  const [scans, setScans] = useState<HistoryScan[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedForCompare, setSelectedForCompare] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingNotesId, setEditingNotesId] = useState<string | null>(null);
  const [editingNotesValue, setEditingNotesValue] = useState('');
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [scanToDelete, setScanToDelete] = useState<string | null>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Keyboard shortcuts
  useKeyboardShortcuts([
    {
      key: 'k',
      ctrl: true,
      handler: () => {
        searchInputRef.current?.focus();
        searchInputRef.current?.select();
      },
      description: 'Focus search'
    },
    {
      key: '/',
      handler: () => {
        searchInputRef.current?.focus();
        searchInputRef.current?.select();
      },
      description: 'Focus search'
    },
    {
      key: 'e',
      ctrl: true,
      shift: false,
      handler: () => {
        if (scans.length > 0) {
          exportToJSON();
        }
      },
      description: 'Export as JSON'
    },
    {
      key: 'e',
      ctrl: true,
      shift: true,
      handler: () => {
        if (scans.length > 0) {
          exportToCSV();
        }
      },
      description: 'Export as CSV'
    },
  ]);

  useEffect(() => {
    loadHistory();
  }, [currentScanId]);

  const loadHistory = async () => {
    try {
      const response = await fetch('/api/history?limit=10');
      if (response.ok) {
        const data = await response.json();
        setScans(data.scans || []);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  const openDeleteModal = (scanId: string) => {
    setScanToDelete(scanId);
    setDeleteModalOpen(true);
  };

  const confirmDelete = async () => {
    if (!scanToDelete) return;

    try {
      const response = await fetch(`/api/history/${scanToDelete}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setScans(scans.filter(s => s.id !== scanToDelete));
        if (selectedForCompare === scanToDelete) {
          setSelectedForCompare(null);
        }
      }
    } catch (error) {
      console.error('Failed to delete scan:', error);
    }

    setDeleteModalOpen(false);
    setScanToDelete(null);
  };

  const cancelDelete = () => {
    setDeleteModalOpen(false);
    setScanToDelete(null);
  };

  const handleCompareSelect = (scanId: string) => {
    if (selectedForCompare === scanId) {
      setSelectedForCompare(null);
    } else if (selectedForCompare === null) {
      setSelectedForCompare(scanId);
    } else {
      // Both scans selected, trigger comparison
      if (onCompare) {
        onCompare(selectedForCompare, scanId);
      }
      setSelectedForCompare(null);
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
  };

  const getTrend = (current: HistoryScan, previous?: HistoryScan) => {
    if (!previous) return null;

    const vulnDiff = current.summary.vulnerabilities - previous.summary.vulnerabilities;
    const outdatedDiff = current.summary.outdated_packages - previous.summary.outdated_packages;

    if (vulnDiff < 0 || outdatedDiff < 0) {
      return { type: 'improving', icon: TrendingDown, color: 'text-primary-600 dark:text-primary-400' };
    } else if (vulnDiff > 0 || outdatedDiff > 0) {
      return { type: 'worsening', icon: TrendingUp, color: 'text-red-600 dark:text-red-400' };
    }
    return null;
  };

  const exportToJSON = () => {
    const dataStr = JSON.stringify(scans, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `devaudit-history-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportToCSV = () => {
    const headers = ['Date', 'Scan ID', 'Total Packages', 'Outdated', 'Vulnerabilities', 'Cleanup Items', 'Tools Detected'];
    const rows = scans.map(scan => [
      new Date(scan.timestamp).toLocaleString(),
      scan.id,
      scan.summary.total_packages,
      scan.summary.outdated_packages,
      scan.summary.vulnerabilities,
      scan.summary.cleanup_items,
      scan.summary.tools_detected,
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const dataBlob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `devaudit-history-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Filter scans based on search query
  const filteredScans = scans.filter(scan => {
    if (!searchQuery) return true;

    const query = searchQuery.toLowerCase();
    const date = new Date(scan.timestamp).toLocaleString().toLowerCase();
    const id = scan.id.toLowerCase();
    const notes = scan.metadata?.notes?.toLowerCase() || '';

    return (
      date.includes(query) ||
      id.includes(query) ||
      notes.includes(query) ||
      scan.summary.total_packages.toString().includes(query) ||
      scan.summary.outdated_packages.toString().includes(query) ||
      scan.summary.vulnerabilities.toString().includes(query)
    );
  });

  const startEditingNotes = (scan: HistoryScan) => {
    setEditingNotesId(scan.id);
    setEditingNotesValue(scan.metadata?.notes || '');
  };

  const saveNotes = async (scanId: string) => {
    try {
      const response = await fetch(`/api/history/${scanId}/notes`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ notes: editingNotesValue }),
      });

      if (response.ok) {
        // Update local state
        setScans(scans.map(scan =>
          scan.id === scanId
            ? { ...scan, metadata: { ...scan.metadata, notes: editingNotesValue } }
            : scan
        ));
        setEditingNotesId(null);
        setEditingNotesValue('');
      } else {
        alert('Failed to save notes');
      }
    } catch (error) {
      console.error('Failed to save notes:', error);
      alert('Failed to save notes');
    }
  };

  const cancelEditingNotes = () => {
    setEditingNotesId(null);
    setEditingNotesValue('');
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border border-gray-200 dark:border-dark-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 bg-gray-200 dark:bg-dark-700 rounded animate-pulse"></div>
            <div className="h-5 w-32 bg-gray-200 dark:bg-dark-700 rounded animate-pulse"></div>
          </div>
          <div className="flex gap-1">
            <div className="h-7 w-16 bg-gray-200 dark:bg-dark-700 rounded animate-pulse"></div>
            <div className="h-7 w-16 bg-gray-200 dark:bg-dark-700 rounded animate-pulse"></div>
          </div>
        </div>

        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-gray-50 dark:bg-dark-700 rounded-lg border border-gray-200 dark:border-dark-600 p-4 animate-pulse">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-4 h-4 bg-gray-200 dark:bg-dark-600 rounded"></div>
                <div className="h-4 w-24 bg-gray-200 dark:bg-dark-600 rounded"></div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="h-3 bg-gray-200 dark:bg-dark-600 rounded"></div>
                <div className="h-3 bg-gray-200 dark:bg-dark-600 rounded"></div>
                <div className="h-3 bg-gray-200 dark:bg-dark-600 rounded"></div>
                <div className="h-3 bg-gray-200 dark:bg-dark-600 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (scans.length === 0) {
    return (
      <div className="bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border border-gray-200 dark:border-dark-700 p-6">
        <div className="flex items-center gap-2 mb-3">
          <Clock className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Scan History</h3>
        </div>
        <p className="text-gray-500 dark:text-gray-400 text-sm">
          No scan history yet. Run a scan to start tracking your environment over time.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border border-gray-200 dark:border-dark-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Scan History</h3>
          <span className="text-xs text-gray-500 dark:text-gray-400">({scans.length} scans)</span>
        </div>
        <div className="flex items-center gap-2">
          {selectedForCompare ? (
            <div className="text-xs text-blue-600 dark:text-blue-400 font-medium">
              Select another scan to compare
            </div>
          ) : scans.length > 0 && (
            <div className="flex items-center gap-1">
              <button
                onClick={exportToJSON}
                className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 text-gray-700 dark:text-gray-300 rounded transition-colors"
                title="Export as JSON (Ctrl+E)"
              >
                <FileJson className="w-3.5 h-3.5" />
                <span>JSON</span>
                <kbd className="ml-1 px-1 py-0.5 bg-gray-200 dark:bg-dark-600 border border-gray-300 dark:border-dark-500 rounded text-xs font-mono opacity-60">⌘E</kbd>
              </button>
              <button
                onClick={exportToCSV}
                className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 text-gray-700 dark:text-gray-300 rounded transition-colors"
                title="Export as CSV (Ctrl+Shift+E)"
              >
                <FileText className="w-3.5 h-3.5" />
                <span>CSV</span>
                <kbd className="ml-1 px-1 py-0.5 bg-gray-200 dark:bg-dark-600 border border-gray-300 dark:border-dark-500 rounded text-xs font-mono opacity-60">⌘⇧E</kbd>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Search Bar */}
      {scans.length > 0 && (
        <div className="mb-4 relative">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search scans by date, ID, or metrics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-10 py-2 text-sm bg-gray-50 dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
            />
            <div className="absolute right-10 top-1/2 transform -translate-y-1/2 text-xs text-gray-400 dark:text-gray-500 pointer-events-none">
              <kbd className="px-1.5 py-0.5 bg-gray-100 dark:bg-dark-600 border border-gray-300 dark:border-dark-500 rounded text-xs font-mono">/</kbd>
            </div>
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          {searchQuery && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Found {filteredScans.length} of {scans.length} scans
            </p>
          )}
        </div>
      )}

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredScans.map((scan, index) => {
          const trend = index < filteredScans.length - 1 ? getTrend(scan, filteredScans[index + 1]) : null;
          const isCurrentScan = scan.id === currentScanId;
          const isSelectedForCompare = scan.id === selectedForCompare;
          const TrendIcon = trend?.icon;

          return (
            <div
              key={scan.id}
              className={`relative p-4 rounded-lg border transition-all ${
                isCurrentScan
                  ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-300 dark:border-primary-700'
                  : isSelectedForCompare
                  ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700'
                  : 'bg-gray-50 dark:bg-dark-700 border-gray-200 dark:border-dark-600 hover:border-gray-300 dark:hover:border-dark-500'
              }`}
            >
              {/* Timeline Dot */}
              {index < scans.length - 1 && (
                <div className="absolute left-2 top-full h-2 w-px bg-gray-300 dark:bg-dark-600"></div>
              )}

              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  {/* Header */}
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {formatDate(scan.timestamp)}
                    </span>
                    {isCurrentScan && (
                      <span className="px-2 py-0.5 bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300 text-xs rounded-full border border-primary-200 dark:border-primary-800">
                        Current
                      </span>
                    )}
                    {trend && TrendIcon && (
                      <TrendIcon className={`w-4 h-4 ${trend.color}`} />
                    )}
                  </div>

                  {/* Stats - Compact inline layout */}
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs">
                    <div className="flex items-center gap-1">
                      <span className="text-gray-600 dark:text-gray-400">Packages:</span>
                      <span className="font-semibold text-gray-900 dark:text-gray-100">
                        {scan.summary.total_packages}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-gray-600 dark:text-gray-400">Outdated:</span>
                      <span className={`font-semibold ${
                        scan.summary.outdated_packages > 0
                          ? 'text-yellow-600 dark:text-yellow-400'
                          : 'text-gray-900 dark:text-gray-100'
                      }`}>
                        {scan.summary.outdated_packages}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-gray-600 dark:text-gray-400">Vulnerabilities:</span>
                      <span className={`font-semibold ${
                        scan.summary.vulnerabilities > 0
                          ? 'text-red-600 dark:text-red-400'
                          : 'text-primary-600 dark:text-primary-400'
                      }`}>
                        {scan.summary.vulnerabilities}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-gray-600 dark:text-gray-400">Tools:</span>
                      <span className="font-semibold text-gray-900 dark:text-gray-100">
                        {scan.summary.tools_detected}
                      </span>
                    </div>
                  </div>

                  {/* Notes */}
                  {editingNotesId === scan.id ? (
                    <div className="mt-2">
                      <input
                        type="text"
                        value={editingNotesValue}
                        onChange={(e) => setEditingNotesValue(e.target.value)}
                        placeholder="Add notes (e.g., 'before upgrade', 'production audit')..."
                        className="w-full px-2 py-1 text-xs bg-white dark:bg-dark-600 border border-blue-300 dark:border-blue-600 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 text-gray-900 dark:text-gray-100"
                        autoFocus
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            saveNotes(scan.id);
                          } else if (e.key === 'Escape') {
                            cancelEditingNotes();
                          }
                        }}
                      />
                      <div className="flex items-center gap-1 mt-1">
                        <button
                          onClick={() => saveNotes(scan.id)}
                          className="flex items-center gap-1 px-2 py-0.5 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
                        >
                          <Save className="w-3 h-3" />
                          Save
                        </button>
                        <button
                          onClick={cancelEditingNotes}
                          className="px-2 py-0.5 text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
                        >
                          Cancel
                        </button>
                        <span className="text-xs text-gray-400 dark:text-gray-500 ml-auto">
                          Press Enter to save, Esc to cancel
                        </span>
                      </div>
                    </div>
                  ) : scan.metadata?.notes ? (
                    <div className="mt-2 flex items-start gap-1">
                      <Tag className="w-3 h-3 text-gray-400 mt-0.5 flex-shrink-0" />
                      <p className="text-xs text-gray-600 dark:text-gray-400 italic flex-1">
                        {scan.metadata.notes}
                      </p>
                      <button
                        onClick={() => startEditingNotes(scan)}
                        className="p-0.5 hover:bg-gray-200 dark:hover:bg-dark-600 rounded transition-colors"
                        title="Edit notes"
                      >
                        <Edit2 className="w-3 h-3 text-gray-500 dark:text-gray-400" />
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => startEditingNotes(scan)}
                      className="mt-2 flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                    >
                      <Tag className="w-3 h-3" />
                      Add notes...
                    </button>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleCompareSelect(scan.id)}
                    className={`p-2 rounded hover:bg-gray-200 dark:hover:bg-dark-600 transition-colors ${
                      isSelectedForCompare ? 'bg-blue-100 dark:bg-blue-900/40' : ''
                    }`}
                    title="Compare scans"
                  >
                    <GitCompare className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  </button>
                  <button
                    onClick={() => openDeleteModal(scan.id)}
                    className="p-2 rounded hover:bg-red-100 dark:hover:bg-red-900/20 transition-colors"
                    title={isCurrentScan ? "Delete current scan" : "Delete scan"}
                  >
                    <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {scans.length >= 20 && (
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-3 text-center">
          Showing {scans.length} most recent scans
        </p>
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={deleteModalOpen}
        title="Delete Scan?"
        message={
          scanToDelete === currentScanId
            ? "Are you sure you want to delete the current scan? This will remove all scan data and history for this session."
            : "Are you sure you want to delete this scan? This action cannot be undone."
        }
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
        variant="danger"
      />
    </div>
  );
}
