'use client';

import { useState } from 'react';
import { ChevronLeft, ChevronRight, Shield, Activity, Lock, Cpu } from 'lucide-react';
import { SystemAuditorCard } from './SystemAuditorCard';

interface SystemAuditorCarouselProps {
  data: any;
}

interface SystemAuditor {
  key: string;
  title: string;
  data: any;
  icon: 'shield' | 'alert' | 'check' | 'x' | 'info';
}

export function SystemAuditorCarousel({ data }: SystemAuditorCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Helper function to validate auditor data
  const isValidAuditor = (auditorData: any): boolean => {
    if (!auditorData || typeof auditorData !== 'object') {
      return false;
    }
    // Only include auditors that are installed and have valid data
    // Allow 'installed' to be undefined (default to true) for backward compatibility
    if (auditorData.installed === false) {
      return false;
    }
    // Must have at least a risk_level or some indication of valid data
    return auditorData.risk_level !== undefined || auditorData.recommendation !== undefined;
  };

  // Build list of available system auditors with validation
  const auditors: SystemAuditor[] = [];

  if (data['OS Updates'] && isValidAuditor(data['OS Updates'])) {
    auditors.push({
      key: 'OS Updates',
      title: 'OS Updates',
      data: data['OS Updates'],
      icon: 'shield'
    });
  }

  if (data['Antivirus'] && isValidAuditor(data['Antivirus'])) {
    auditors.push({
      key: 'Antivirus',
      title: 'Antivirus',
      data: data['Antivirus'],
      icon: 'shield'
    });
  }

  if (data['Firewall'] && isValidAuditor(data['Firewall'])) {
    auditors.push({
      key: 'Firewall',
      title: 'Firewall',
      data: data['Firewall'],
      icon: 'shield'
    });
  }

  if (data['BIOS/UEFI'] && isValidAuditor(data['BIOS/UEFI'])) {
    auditors.push({
      key: 'BIOS/UEFI',
      title: 'BIOS/UEFI',
      data: data['BIOS/UEFI'],
      icon: 'info'
    });
  }

  if (data['Driver Updates'] && isValidAuditor(data['Driver Updates'])) {
    auditors.push({
      key: 'Driver Updates',
      title: 'Driver Updates',
      data: data['Driver Updates'],
      icon: 'shield'
    });
  }

  if (data['Disk Health'] && isValidAuditor(data['Disk Health'])) {
    auditors.push({
      key: 'Disk Health',
      title: 'Disk Health',
      data: data['Disk Health'],
      icon: 'shield'
    });
  }

  if (data['Backup Status'] && isValidAuditor(data['Backup Status'])) {
    auditors.push({
      key: 'Backup Status',
      title: 'Backup Status',
      data: data['Backup Status'],
      icon: 'shield'
    });
  }

  if (data['Disk Encryption'] && isValidAuditor(data['Disk Encryption'])) {
    auditors.push({
      key: 'Disk Encryption',
      title: 'Disk Encryption',
      data: data['Disk Encryption'],
      icon: 'shield'
    });
  }

  // Empty state
  if (auditors.length === 0) {
    return (
      <div className="bg-white dark:bg-dark-800 rounded-lg shadow-md border border-gray-200 dark:border-dark-700 p-8">
        <div className="text-center">
          <Shield className="w-12 h-12 text-gray-400 dark:text-gray-600 mx-auto mb-3" />
          <p className="text-gray-600 dark:text-gray-400 font-medium mb-2">
            No System Auditors Available
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500">
            Run a scan to see system security status
          </p>
        </div>
      </div>
    );
  }

  const totalSlides = auditors.length;
  const cardsPerView = {
    mobile: 1,
    tablet: 2,
    desktop: 3
  };

  // Ensure currentIndex is within bounds (in case auditors change dynamically)
  const safeCurrentIndex = Math.min(currentIndex, totalSlides - 1);

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % totalSlides);
  };

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + totalSlides) % totalSlides);
  };

  const goToSlide = (index: number) => {
    if (index >= 0 && index < totalSlides) {
      setCurrentIndex(index);
    }
  };

  // Get visible cards centered around current index
  const getVisibleCards = (cardsToShow: number) => {
    const cards = [];

    // For 3 cards (desktop): center the active card by showing [currentIndex-1, currentIndex, currentIndex+1]
    // For 2 cards (tablet): show [currentIndex, currentIndex+1]
    // For 1 card (mobile): show [currentIndex]

    const startOffset = cardsToShow === 3 ? -1 : 0; // Center for 3 cards, left-align for others

    for (let i = 0; i < cardsToShow && i < totalSlides; i++) {
      const index = (safeCurrentIndex + startOffset + i + totalSlides) % totalSlides;
      // Additional safety check
      if (index >= 0 && index < auditors.length && auditors[index]) {
        cards.push(auditors[index]);
      }
    }
    return cards;
  };

  return (
    <div className="space-y-6">
      {/* Summary Indicators */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {auditors.map((auditor, index) => {
          const riskLevel = auditor.data?.risk_level || 'none';
          const icon = getAuditorIcon(auditor.title);
          const color = getRiskColor(riskLevel);

          return (
            <button
              key={auditor.key}
              onClick={() => goToSlide(index)}
              className={`p-3 rounded-lg border-2 transition-all hover:shadow-md ${
                safeCurrentIndex === index
                  ? `${color.border} ${color.bg} ring-2 ring-offset-2 ${color.ring}`
                  : 'border-gray-200 dark:border-dark-600 bg-white dark:bg-dark-800'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                {icon}
                <span className="text-xs font-semibold text-gray-700 dark:text-gray-300 truncate">
                  {auditor.title}
                </span>
              </div>
              <div className={`text-xs font-bold uppercase ${color.text}`}>
                {riskLevel}
              </div>
            </button>
          );
        })}
      </div>

      {/* Carousel Container with fixed arrow positioning */}
      <div className="relative">
        {/* Navigation Arrows - Fixed at 200px from top (center of cards) */}
        {totalSlides > 1 && (
          <>
            <button
              onClick={prevSlide}
              className="absolute left-0 top-[200px] -translate-y-1/2 -translate-x-4 z-10 bg-white dark:bg-dark-800 border-2 border-gray-300 dark:border-dark-600 rounded-full p-2 shadow-lg hover:bg-gray-50 dark:hover:bg-dark-700 transition-all"
              aria-label="Previous card"
            >
              <ChevronLeft className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            </button>

            <button
              onClick={nextSlide}
              className="absolute right-0 top-[200px] -translate-y-1/2 translate-x-4 z-10 bg-white dark:bg-dark-800 border-2 border-gray-300 dark:border-dark-600 rounded-full p-2 shadow-lg hover:bg-gray-50 dark:hover:bg-dark-700 transition-all"
              aria-label="Next card"
            >
              <ChevronRight className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            </button>
          </>
        )}

        {/* Cards Grid - Responsive */}
        <div className="overflow-hidden">
          {/* Mobile: 1 card */}
          <div className="md:hidden">
            {auditors[safeCurrentIndex] && (
              <SystemAuditorCard
                title={auditors[safeCurrentIndex].title}
                data={auditors[safeCurrentIndex].data}
                icon={auditors[safeCurrentIndex].icon}
              />
            )}
          </div>

          {/* Tablet: 2 cards */}
          <div className="hidden md:grid lg:hidden grid-cols-2 gap-6">
            {getVisibleCards(2).map((auditor) => (
              <SystemAuditorCard
                key={auditor.key}
                title={auditor.title}
                data={auditor.data}
                icon={auditor.icon}
              />
            ))}
          </div>

          {/* Desktop: 3 cards with center card subtly highlighted */}
          <div className="hidden lg:grid grid-cols-3 gap-6">
            {getVisibleCards(3).map((auditor, idx) => {
              const isCenter = idx === 1; // Middle card in 3-card view
              return (
                <div key={auditor.key} className={`transition-all ${isCenter ? 'ring-2 ring-primary-500 dark:ring-primary-400 ring-offset-2 dark:ring-offset-dark-900' : ''}`}>
                  <SystemAuditorCard
                    title={auditor.title}
                    data={auditor.data}
                    icon={auditor.icon}
                  />
                </div>
              );
            })}
          </div>
        </div>

        {/* Carousel Dots */}
        {totalSlides > 1 && (
          <div className="flex justify-center gap-2 mt-6">
            {auditors.map((_, index) => (
              <button
                key={index}
                onClick={() => goToSlide(index)}
                className={`h-2 rounded-full transition-all ${
                  index === safeCurrentIndex
                    ? 'w-8 bg-primary-600 dark:bg-primary-400'
                    : 'w-2 bg-gray-300 dark:bg-dark-600 hover:bg-gray-400 dark:hover:bg-dark-500'
                }`}
                aria-label={`Go to slide ${index + 1}`}
              />
            ))}
          </div>
        )}
      </div>

      {/* Info Text */}
      <div className="text-center">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Showing {safeCurrentIndex + 1} of {totalSlides} system auditors
        </p>
      </div>
    </div>
  );
}

function getAuditorIcon(title: string) {
  const iconClass = "w-4 h-4";

  switch (title) {
    case 'OS Updates':
      return <Shield className={iconClass} />;
    case 'Antivirus':
      return <Activity className={iconClass} />;
    case 'Firewall':
      return <Lock className={iconClass} />;
    case 'BIOS/UEFI':
      return <Cpu className={iconClass} />;
    default:
      return <Shield className={iconClass} />;
  }
}

function getRiskColor(riskLevel: string) {
  const colors = {
    critical: {
      bg: 'bg-red-50 dark:bg-red-900/20',
      border: 'border-red-500 dark:border-red-400',
      ring: 'ring-red-500 dark:ring-red-400',
      text: 'text-red-600 dark:text-red-400'
    },
    high: {
      bg: 'bg-orange-50 dark:bg-orange-900/20',
      border: 'border-orange-500 dark:border-orange-400',
      ring: 'ring-orange-500 dark:ring-orange-400',
      text: 'text-orange-600 dark:text-orange-400'
    },
    medium: {
      bg: 'bg-yellow-50 dark:bg-yellow-900/20',
      border: 'border-yellow-500 dark:border-yellow-400',
      ring: 'ring-yellow-500 dark:ring-yellow-400',
      text: 'text-yellow-600 dark:text-yellow-400'
    },
    low: {
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      border: 'border-blue-500 dark:border-blue-400',
      ring: 'ring-blue-500 dark:ring-blue-400',
      text: 'text-blue-600 dark:text-blue-400'
    },
    none: {
      bg: 'bg-green-50 dark:bg-green-900/20',
      border: 'border-green-500 dark:border-green-400',
      ring: 'ring-green-500 dark:ring-green-400',
      text: 'text-green-600 dark:text-green-400'
    }
  };

  return colors[riskLevel as keyof typeof colors] || colors.none;
}
