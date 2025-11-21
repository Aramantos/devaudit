'use client';

import { Shield, AlertTriangle, CheckCircle, XCircle, Info } from 'lucide-react';

interface SystemAuditorCardProps {
  title: string;
  data: any;
  icon?: 'shield' | 'alert' | 'check' | 'x' | 'info';
}

export function SystemAuditorCard({ title, data, icon = 'shield' }: SystemAuditorCardProps) {
  if (!data || !data.installed) {
    return null;
  }

  // Determine risk color
  const riskLevel = data.risk_level || 'none';
  const riskColors = {
    critical: 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
    high: 'text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800',
    medium: 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800',
    low: 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
    none: 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
  };

  const cardColor = riskColors[riskLevel as keyof typeof riskColors] || riskColors.none;

  // Choose icon
  const IconComponent = icon === 'shield' ? Shield :
                       icon === 'alert' ? AlertTriangle :
                       icon === 'check' ? CheckCircle :
                       icon === 'x' ? XCircle : Info;

  return (
    <div className={`rounded-lg border-2 p-6 ${cardColor} transition-all hover:shadow-lg flex flex-col min-h-[15rem]`} style={{ height: '-webkit-fill-available' }}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <IconComponent className="w-6 h-6" />
          <h3 className="text-lg font-semibold">{title}</h3>
        </div>
        {riskLevel !== 'none' && (
          <span className="px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide bg-white/50 dark:bg-black/20">
            {riskLevel}
          </span>
        )}
      </div>

      {/* Information Section - Always present, consistent height */}
      <div className="space-y-2 mb-4 text-sm min-h-[140px]">
        {/* OS Updates Specific */}
        {data.os_name && (
          <div>
            <span className="font-medium">OS:</span> {data.os_name} {data.os_version}
          </div>
        )}
        {data.update_count !== undefined && (
          <div>
            <span className="font-medium">Pending Updates:</span> {data.update_count}
            {data.security_updates > 0 && (
              <span className="ml-2 text-red-600 dark:text-red-400 font-semibold">
                ({data.security_updates} security)
              </span>
            )}
          </div>
        )}

        {/* Antivirus Specific */}
        {data.products && data.products.length > 0 && (
          <>
            <div>
              <span className="font-medium">Product:</span> {data.products[0].name}
            </div>
            <div>
              <span className="font-medium">Status:</span>{' '}
              {data.enabled ? (
                <span className="text-green-600 dark:text-green-400">Enabled</span>
              ) : (
                <span className="text-red-600 dark:text-red-400">Disabled</span>
              )}
            </div>
            <div>
              <span className="font-medium">Definitions:</span>{' '}
              {data.updated ? (
                <span className="text-green-600 dark:text-green-400">Up-to-date</span>
              ) : (
                <span className="text-orange-600 dark:text-orange-400">Outdated</span>
              )}
            </div>
          </>
        )}

        {/* Firewall Specific */}
        {data.firewall_type && (
          <>
            <div>
              <span className="font-medium">Type:</span> {data.firewall_type}
            </div>
            <div>
              <span className="font-medium">Status:</span>{' '}
              {data.enabled ? (
                <span className="text-green-600 dark:text-green-400">Enabled</span>
              ) : (
                <span className="text-red-600 dark:text-red-400">Disabled</span>
              )}
            </div>
            {data.profiles && data.profiles.length > 0 && (
              <div>
                <span className="font-medium">Profiles:</span>{' '}
                <span className="inline-flex gap-2 ml-1">
                  {data.profiles.map((profile: any, idx: number) => (
                    <span key={idx} className="text-xs">
                      {profile.name}:{' '}
                      {profile.enabled ? (
                        <span className="text-green-600 dark:text-green-400">ON</span>
                      ) : (
                        <span className="text-red-600 dark:text-red-400">OFF</span>
                      )}
                    </span>
                  ))}
                </span>
              </div>
            )}
          </>
        )}

        {/* BIOS Specific */}
        {data.vendor && (
          <>
            <div>
              <span className="font-medium">Vendor:</span> {data.vendor}
            </div>
            <div>
              <span className="font-medium">Version:</span> {data.version}
            </div>
            {data.age_days !== undefined && data.age_days !== null && (
              <div>
                <span className="font-medium">Age:</span> {data.age_days} days old
              </div>
            )}
          </>
        )}

        {/* Disk Health Specific */}
        {data.disks && data.disks.length > 0 && (
          <>
            <div>
              <span className="font-medium">Monitored Disks:</span> {data.disks.length}
              {data.small_drives_skipped > 0 && (
                <span className="text-xs ml-1 opacity-75">
                  ({data.small_drives_skipped} small drive{data.small_drives_skipped > 1 ? 's' : ''} excluded)
                </span>
              )}
            </div>
            {data.disks.slice(0, 3).map((disk: any, idx: number) => (
              <div key={idx} className="text-xs ml-2">
                {disk.name} {disk.percent_used >= 85 ? (
                  <span className="text-orange-600 dark:text-orange-400 font-semibold">
                    {disk.percent_used}% used
                  </span>
                ) : (
                  <span className="opacity-75">{disk.percent_used}% used</span>
                )} ({disk.free_gb}GB free)
              </div>
            ))}
            {data.disks.length > 3 && (
              <div className="text-xs ml-2 opacity-75">
                +{data.disks.length - 3} more drive{data.disks.length > 4 ? 's' : ''}
              </div>
            )}
          </>
        )}

        {/* Backup Status Specific */}
        {(data.backup_configured !== undefined || data.backup_systems) && (
          <>
            <div>
              <span className="font-medium">Backup Configured:</span>{' '}
              {data.backup_configured ? (
                <span className="text-green-600 dark:text-green-400">Yes</span>
              ) : (
                <span className="text-red-600 dark:text-red-400">No</span>
              )}
            </div>
            {data.backup_systems && data.backup_systems.length > 0 ? (
              <>
                <div>
                  <span className="font-medium">Systems Found:</span> {data.backup_systems.length}
                </div>
                {data.backup_systems.slice(0, 2).map((system: any, idx: number) => (
                  <div key={idx} className="text-xs ml-2">
                    {system.name}: {system.status}
                  </div>
                ))}
              </>
            ) : (
              <div className="text-sm opacity-75">
                No backup systems detected
              </div>
            )}
          </>
        )}

        {/* Disk Encryption Specific */}
        {(data.encryption_enabled !== undefined || data.encryption_type) && (
          <>
            <div>
              <span className="font-medium">Encryption:</span>{' '}
              {data.status_unknown ? (
                <span className="text-yellow-600 dark:text-yellow-400">Unknown</span>
              ) : data.encryption_enabled ? (
                <span className="text-green-600 dark:text-green-400">Enabled</span>
              ) : (
                <span className="text-red-600 dark:text-red-400">Disabled</span>
              )}
            </div>
            {data.encryption_type && data.encryption_type !== 'None' && (
              <div>
                <span className="font-medium">Type:</span> {data.encryption_type}
              </div>
            )}
            {data.encrypted_volumes && data.encrypted_volumes.length > 0 && (
              <div>
                <span className="font-medium">Protected Volumes:</span> {data.encrypted_volumes.length}
              </div>
            )}
            {data.unencrypted_volumes > 0 && (
              <div className="text-xs text-orange-600 dark:text-orange-400">
                {data.unencrypted_volumes} unencrypted volume{data.unencrypted_volumes > 1 ? 's' : ''}
              </div>
            )}
          </>
        )}

        {/* Driver Updates Specific */}
        {(data.drivers_checked !== undefined || data.critical_drivers) && (
          <>
            <div>
              <span className="font-medium">Drivers Checked:</span> {data.drivers_checked || 0}
            </div>
            {data.outdated_critical > 0 && (
              <div className="text-xs text-red-600 dark:text-red-400 font-semibold">
                {data.outdated_critical} critical driver{data.outdated_critical > 1 ? 's' : ''} outdated
              </div>
            )}
            {data.oldest_driver_age_days > 0 && (
              <div>
                <span className="font-medium">Oldest Driver:</span>{' '}
                {Math.floor(data.oldest_driver_age_days / 365)} year{Math.floor(data.oldest_driver_age_days / 365) !== 1 ? 's' : ''} old
              </div>
            )}
            {data.critical_drivers && data.critical_drivers.length > 0 && (
              <div className="text-xs mt-2 opacity-75">
                Recent: {data.critical_drivers[0]?.device_name || 'Unknown'}
              </div>
            )}
          </>
        )}
      </div>

      {/* Warnings */}
      {data.warnings && data.warnings.length > 0 && (
        <div className="mt-3 text-xs opacity-75">
          {data.warnings.map((warning: string, idx: number) => (
            <div key={idx}>⚠️ {warning}</div>
          ))}
        </div>
      )}
    </div>
  );
}
