import { Modal } from './Modal';
import { Keyboard, Search, Download, FileJson, FileText, X } from 'lucide-react';

interface KeyboardShortcutsHelpProps {
  isOpen: boolean;
  onClose: () => void;
}

export function KeyboardShortcutsHelp({ isOpen, onClose }: KeyboardShortcutsHelpProps) {
  // navigator does not exist during Next.js static prerender - default to Ctrl.
  const modKey = typeof navigator !== 'undefined' && navigator.platform.toLowerCase().includes('mac') ? '⌘' : 'Ctrl';

  const shortcuts = [
    {
      category: 'Navigation',
      items: [
        { keys: ['/', `${modKey}+K`], description: 'Focus search', icon: <Search className="w-4 h-4" /> },
        { keys: ['Esc'], description: 'Clear search / Close modal', icon: <X className="w-4 h-4" /> },
      ]
    },
    {
      category: 'Actions',
      items: [
        { keys: [`${modKey}+E`], description: 'Export as JSON', icon: <FileJson className="w-4 h-4" /> },
        { keys: [`${modKey}+Shift+E`], description: 'Export as CSV', icon: <FileText className="w-4 h-4" /> },
      ]
    },
    {
      category: 'Notes',
      items: [
        { keys: ['Enter'], description: 'Save notes (when editing)', icon: null },
        { keys: ['Esc'], description: 'Cancel notes editing', icon: null },
      ]
    },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Keyboard Shortcuts">
      <div className="space-y-6">
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <Keyboard className="w-4 h-4" />
          <p>Use these keyboard shortcuts to navigate faster</p>
        </div>

        {shortcuts.map((section, idx) => (
          <div key={idx}>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">
              {section.category}
            </h3>
            <div className="space-y-2">
              {section.items.map((item, itemIdx) => (
                <div
                  key={itemIdx}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-700 rounded-lg border border-gray-200 dark:border-dark-600"
                >
                  <div className="flex items-center gap-2">
                    {item.icon && (
                      <div className="text-gray-500 dark:text-gray-400">
                        {item.icon}
                      </div>
                    )}
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {item.description}
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    {item.keys.map((key, keyIdx) => (
                      <div key={keyIdx} className="flex items-center gap-1">
                        {keyIdx > 0 && (
                          <span className="text-xs text-gray-400 dark:text-gray-500">or</span>
                        )}
                        <kbd className="px-2 py-1 bg-white dark:bg-dark-800 border border-gray-300 dark:border-dark-500 rounded text-xs font-mono text-gray-700 dark:text-gray-300 shadow-sm">
                          {key}
                        </kbd>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        <div className="pt-4 border-t border-gray-200 dark:border-dark-600">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Press <kbd className="px-1.5 py-0.5 bg-gray-100 dark:bg-dark-700 border border-gray-300 dark:border-dark-500 rounded text-xs font-mono">?</kbd> to toggle this help
          </p>
        </div>
      </div>
    </Modal>
  );
}
