import { Wifi, WifiOff, Loader } from 'lucide-react';

interface RealtimeStatusProps {
  connected: boolean;
  scanning?: boolean;
  progress?: {
    current: number;
    total: number;
  };
}

export function RealtimeStatus({ connected, scanning, progress }: RealtimeStatusProps) {
  return (
    <div className="mt-4 flex items-center gap-4 text-sm">
      {/* Connection Status */}
      <div className="flex items-center gap-2">
        {connected ? (
          <>
            <Wifi className="w-4 h-4 text-blue-500 dark:text-blue-400" />
            <span className="text-blue-600 dark:text-blue-400 font-medium">Connected</span>
          </>
        ) : (
          <>
            <WifiOff className="w-4 h-4 text-red-500 dark:text-red-400" />
            <span className="text-red-600 dark:text-red-400 font-medium">Disconnected</span>
          </>
        )}
      </div>

      {/* Scan Progress */}
      {scanning && progress && progress.total > 0 && (
        <div className="flex items-center gap-2">
          <Loader className="w-4 h-4 text-blue-500 dark:text-blue-400 animate-spin" />
          <div className="flex items-center gap-2">
            <div className="w-32 bg-gray-200 dark:bg-dark-700 rounded-full h-2">
              <div
                className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{
                  width: `${(progress.current / progress.total) * 100}%`
                }}
              />
            </div>
            <span className="text-gray-600 dark:text-gray-400 font-medium">
              {progress.current}/{progress.total}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
