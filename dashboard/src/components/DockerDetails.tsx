import { Container, AlertTriangle, HardDrive } from 'lucide-react';

interface DockerDetailsProps {
  data: any;
}

export function DockerDetails({ data }: DockerDetailsProps) {
  if (!data?.installed) {
    return (
      <div className="bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border border-gray-200 dark:border-dark-700 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <Container className="w-5 h-5" />
          Docker
        </h2>
        <p className="text-gray-500 dark:text-gray-400">Not installed</p>
      </div>
    );
  }

  const totalContainers = data.container_count || 0;
  const runningContainers = data.running_container_count || 0;
  const totalImages = data.image_count || 0;
  const cleanupCount = data.cleanup_candidates?.length || 0;

  return (
    <div className="bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border border-gray-200 dark:border-dark-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <Container className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          Docker
        </h2>
        <span className="text-sm text-gray-500 dark:text-gray-400">{data.version}</span>
      </div>

      <div className="space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-50 dark:bg-dark-700 border border-gray-100 dark:border-dark-600 rounded p-3">
            <p className="text-sm text-gray-600 dark:text-gray-400">Containers</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {runningContainers}/{totalContainers}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">running/total</p>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded p-3">
            <p className="text-sm text-gray-600 dark:text-gray-400">Images</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{totalImages}</p>
          </div>
        </div>

        {/* Cleanup Candidates */}
        {cleanupCount > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-orange-600 dark:text-orange-400" />
              Cleanup Candidates ({cleanupCount})
            </h3>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {data.cleanup_candidates.slice(0, 5).map((candidate: any, idx: number) => (
                <div key={idx} className="bg-orange-50 dark:bg-orange-900/20 border border-orange-100 dark:border-orange-800 p-3 rounded text-sm">
                  <p className="font-medium text-orange-900 dark:text-orange-300">{candidate.type}</p>
                  <p className="text-orange-700 dark:text-orange-400 text-xs mt-1">
                    {candidate.description}
                  </p>
                  {candidate.size && (
                    <div className="flex items-center gap-1 mt-1 text-orange-600 dark:text-orange-400">
                      <HardDrive className="w-3 h-3" />
                      <span className="text-xs">{candidate.size}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
            {cleanupCount > 5 && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                +{cleanupCount - 5} more
              </p>
            )}
          </div>
        )}

        {/* Large Images */}
        {data.large_images && data.large_images.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-red-600 dark:text-red-400" />
              Large Images
            </h3>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {data.large_images.slice(0, 3).map((image: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between text-sm bg-gray-50 dark:bg-dark-700 border border-gray-100 dark:border-dark-600 p-2 rounded">
                  <span className="font-mono text-xs text-gray-700 dark:text-gray-300 truncate">
                    {image.repository || 'none'}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400 font-medium">
                    {image.size}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
