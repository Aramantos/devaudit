'use client';

import { useState, useEffect } from 'react';
import { Overview } from '@/components/Overview';
import { PythonDetails } from '@/components/PythonDetails';
import { PythonVenvDetails } from '@/components/PythonVenvDetails';
import { NodeDetails } from '@/components/NodeDetails';
import { DockerDetails } from '@/components/DockerDetails';
import { VulnerabilityCard } from '@/components/VulnerabilityCard';
import { SystemSecurityCard } from '@/components/SystemSecurityCard';
import { SystemAuditorCard } from '@/components/SystemAuditorCard';
import { SystemAuditorCarousel } from '@/components/SystemAuditorCarousel';
import { ActionsCard } from '@/components/ActionsCard';
import { ScanHistory } from '@/components/ScanHistory';
import { ComparisonView } from '@/components/ComparisonView';
import { RealtimeStatus } from '@/components/RealtimeStatus';
import { ThemeToggle } from '@/components/ThemeToggle';
import { KeyboardShortcutsHelp } from '@/components/KeyboardShortcutsHelp';
import AIInsightsCard from '@/components/AIInsightsCard';
import { useWebSocket } from '@/lib/websocket';
import { useKeyboardShortcuts } from '@/lib/useKeyboardShortcuts';
import { Play, Loader, HelpCircle, Info } from 'lucide-react';

export default function Dashboard() {
  const [auditData, setAuditData] = useState<any>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState({ current: 0, total: 0 });
  const [currentScanId, setCurrentScanId] = useState<string | null>(null);
  const [comparisonScanIds, setComparisonScanIds] = useState<{ id1: string; id2: string } | null>(null);
  const [showKeyboardHelp, setShowKeyboardHelp] = useState(false);
  const [isHistoricalData, setIsHistoricalData] = useState(false);
  const [scanTimestamp, setScanTimestamp] = useState<string | null>(null);
  const { connected, lastMessage, connect } = useWebSocket();

  // Global keyboard shortcuts
  useKeyboardShortcuts([
    {
      key: '?',
      shift: true,
      handler: () => setShowKeyboardHelp(true),
      description: 'Show keyboard shortcuts help'
    },
  ]);

  // Connect to WebSocket on mount
  useEffect(() => {
    connect();
  }, []);

  // Load latest scan on mount
  useEffect(() => {
    const loadLatestScan = async () => {
      try {
        const response = await fetch('/api/history/latest');
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'success' && data.scan) {
            setAuditData(data.scan.results);
            setCurrentScanId(data.scan.id);
            setScanTimestamp(data.scan.timestamp);
            setIsHistoricalData(true);
          }
        }
      } catch (error) {
        console.log('No previous scans found or error loading:', error);
      }
    };

    loadLatestScan();
  }, []);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage);

        switch (data.type) {
          case 'scan_started':
            setIsScanning(true);
            setScanProgress({ current: 0, total: data.total_auditors || 5 });
            break;

          case 'auditor_started':
            setScanProgress(data.progress);
            break;

          case 'auditor_completed':
            // Update partial results
            setAuditData((prev: any) => ({
              ...prev,
              [data.auditor]: data.data
            }));
            break;

          case 'scan_completed':
            setAuditData(data.results);
            setIsScanning(false);
            setScanProgress({ current: 0, total: 0 });
            setIsHistoricalData(false);
            setScanTimestamp(new Date().toISOString());
            if (data.scan_id) {
              setCurrentScanId(data.scan_id);
            }
            break;

          case 'auditor_error':
            console.error(`Auditor ${data.auditor} error:`, data.error);
            break;
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    }
  }, [lastMessage]);

  const triggerScan = async () => {
    setIsScanning(true);
    setAuditData(null);

    try {
      // Use relative URL since we're served from the same origin
      const response = await fetch('/api/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Scan started:', result);
    } catch (error) {
      console.error('Error triggering scan:', error);
      setIsScanning(false);
      alert('Failed to start scan. Check console for details.');
    }
  };

  const handleCompare = (scanId1: string, scanId2: string) => {
    setComparisonScanIds({ id1: scanId1, id2: scanId2 });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-dark-950 dark:to-dark-900 flex flex-col">
      {/* Header */}
      <header className="bg-white dark:bg-dark-850 border-b border-gray-200 dark:border-dark-700 shadow-sm flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex-1">
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-gray-100 gradient-text">
                DevAudit Dashboard
              </h1>
              <p className="text-sm sm:text-base text-gray-500 dark:text-gray-400 mt-1">
                Local environment auditing and monitoring
              </p>
            </div>

            <div className="flex items-center gap-2 sm:gap-3 w-full sm:w-auto">
              <div className="sm:hidden flex-1">
                <button
                  onClick={triggerScan}
                  disabled={isScanning}
                  className="flex items-center justify-center gap-2 px-4 py-2.5 w-full bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm text-sm font-semibold"
                >
                  {isScanning ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      <span>Scanning...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      <span>Scan</span>
                    </>
                  )}
                </button>
              </div>
              <div className="sm:hidden">
                <ThemeToggle />
              </div>
              <div className="hidden sm:flex items-center gap-3">
                <ThemeToggle />
                <button
                  onClick={triggerScan}
                  disabled={isScanning}
                  className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm min-w-[140px] justify-center"
                >
                  {isScanning ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      <span>Scanning...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      <span>Run Scan</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          <RealtimeStatus
            connected={connected}
            scanning={isScanning}
            progress={scanProgress}
          />

          {/* Historical Data Banner */}
          {isHistoricalData && auditData && (
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <div className="flex items-center gap-2 text-sm">
                <Info className="w-4 h-4 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                <p className="text-blue-700 dark:text-blue-300">
                  <span className="font-semibold">Viewing previous scan</span> from{' '}
                  {scanTimestamp && new Date(scanTimestamp).toLocaleString()} — Click "Run Scan" for fresh data
                </p>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {auditData ? (
          <>
            <Overview data={auditData} />

            {/* Vulnerability Card - Full Width */}
            <div className="mt-6">
              <VulnerabilityCard data={auditData} isScanning={isScanning} />
            </div>

            {/* System Security Card */}
            <div className="mt-6">
              <SystemSecurityCard data={auditData} />
            </div>

            {/* System Auditors Carousel */}
            <div className="mt-6">
              <SystemAuditorCarousel data={auditData} />
            </div>

            {/* AI Insights Card */}
            <div className="mt-6">
              <AIInsightsCard
                scanId={currentScanId || undefined}
                scanResults={auditData ? { results: auditData } : undefined}
              />
            </div>

            {/* Recommended Actions */}
            <div className="mt-6">
              <ActionsCard systemAuditors={auditData} isScanning={isScanning} />
            </div>

            {/* Scan History */}
            <div className="mt-6">
              <ScanHistory currentScanId={currentScanId || undefined} onCompare={handleCompare} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
              {auditData.Python && <PythonDetails data={auditData.Python} />}
              {auditData['Python Environments'] && <PythonVenvDetails data={auditData['Python Environments']} />}
              {auditData['Node.js'] && <NodeDetails data={auditData['Node.js']} />}
              {auditData.Docker && <DockerDetails data={auditData.Docker} />}
              {auditData.Go && (
                <div className="bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border border-gray-200 dark:border-dark-700 p-6">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Go</h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    {auditData.Go.installed ?
                      `Version: ${auditData.Go.version}` :
                      'Not installed'
                    }
                  </p>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full min-h-[400px]">
            <div className="text-center">
              {isScanning ? (
                <>
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-amber-100 dark:bg-amber-900/30 rounded-full mb-4">
                    <Loader className="w-8 h-8 text-amber-600 dark:text-amber-400 animate-spin" />
                  </div>
                  <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    System scan in progress
                  </h2>
                  <p className="text-gray-500 dark:text-gray-400">
                    Analyzing your development tools and packages...
                  </p>
                </>
              ) : (
                <>
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-4">
                    <Play className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                  </div>
                  <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    Ready to audit your environment
                  </h2>
                  <p className="text-gray-500 dark:text-gray-400">
                    Click "Run Scan" to start auditing your development tools and packages
                  </p>
                </>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer - Sticky */}
      <footer className="bg-white dark:bg-dark-850 border-t border-gray-200 dark:border-dark-700 flex-shrink-0 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-gray-500 dark:text-gray-400 text-xs sm:text-sm">
            <div className="text-center sm:text-left">
              <p className="font-semibold text-gray-700 dark:text-gray-300">DevAudit v0.2.0 - Local Mode</p>
              <p className="mt-1 flex items-center justify-center sm:justify-start gap-2">
                <span className="inline-block w-2 h-2 bg-primary-500 rounded-full animate-pulse"></span>
                100% private • All data stays on your machine
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <a
                href="https://github.com/aramantos/devaudit"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                title="View on GitHub"
              >
                GitHub
              </a>
              <a
                href="https://github.com/aramantos/devaudit/blob/main/README.md"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                title="Getting Started Guide"
              >
                Docs
              </a>
              <a
                href="https://github.com/aramantos/devaudit/blob/main/CONTRIBUTING.md"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                title="Contribute to DevAudit"
              >
                Contribute
              </a>
              <button
                onClick={() => setShowKeyboardHelp(true)}
                className="flex items-center gap-1 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                title="Keyboard Shortcuts (Press ?)"
              >
                <HelpCircle className="w-3.5 h-3.5" />
                <span>Shortcuts</span>
              </button>
            </div>
          </div>
        </div>
      </footer>

      {/* Comparison Modal */}
      {comparisonScanIds && (
        <ComparisonView
          scanId1={comparisonScanIds.id1}
          scanId2={comparisonScanIds.id2}
          isOpen={!!comparisonScanIds}
          onClose={() => setComparisonScanIds(null)}
        />
      )}

      {/* Keyboard Shortcuts Help */}
      <KeyboardShortcutsHelp
        isOpen={showKeyboardHelp}
        onClose={() => setShowKeyboardHelp(false)}
      />
    </div>
  );
}
