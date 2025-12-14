'use client';

import { useState, useEffect } from 'react';
import { History, Trash2, Download, Upload, MessageSquare, AlertCircle } from 'lucide-react';
import {
  getChatSessions,
  deleteChatSession,
  deleteAllChatSessions,
  getChatStorageStats,
  exportChatHistory,
  importChatHistory,
  type ChatSession,
} from '@/lib/chatHistory';

interface ChatHistoryPanelProps {
  currentSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onClose: () => void;
}

export default function ChatHistoryPanel({
  currentSessionId,
  onSelectSession,
  onClose,
}: ChatHistoryPanelProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [stats, setStats] = useState({ sessionCount: 0, totalMessages: 0, estimatedSize: '0 KB' });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = () => {
    const allSessions = getChatSessions();
    // Sort by most recent first
    const sorted = allSessions.sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime());
    setSessions(sorted);
    setStats(getChatStorageStats());
  };

  const handleDeleteSession = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent selecting the session
    if (confirm('Delete this chat? This action cannot be undone.')) {
      deleteChatSession(sessionId);
      loadSessions();
    }
  };

  const handleDeleteAll = () => {
    if (showDeleteConfirm) {
      deleteAllChatSessions();
      loadSessions();
      setShowDeleteConfirm(false);
    } else {
      setShowDeleteConfirm(true);
    }
  };

  const handleExport = () => {
    const data = exportChatHistory();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `devaudit-chat-history-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      const success = importChatHistory(content);
      if (success) {
        loadSessions();
        alert('Chat history imported successfully!');
      } else {
        alert('Failed to import chat history. Please check the file format.');
      }
    };
    reader.readAsText(file);
  };

  const formatDate = (date: Date) => {
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

  return (
    <div className="w-64 bg-gray-800 border-l border-gray-700 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-purple-400" />
            <h3 className="text-sm font-semibold text-white">Chat History</h3>
          </div>
        </div>

        {/* Privacy Notice */}
        <div className="mb-3 p-2 bg-blue-900/20 border border-blue-700/50 rounded text-xs">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-3 h-3 text-blue-400 flex-shrink-0 mt-0.5" />
            <p className="text-blue-300">
              All chats stored locally on your device. Not sent to any server.
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="text-xs text-gray-400 space-y-1">
          <div className="flex justify-between">
            <span>Sessions:</span>
            <span className="text-white font-medium">{stats.sessionCount}</span>
          </div>
          <div className="flex justify-between">
            <span>Messages:</span>
            <span className="text-white font-medium">{stats.totalMessages}</span>
          </div>
          <div className="flex justify-between">
            <span>Storage:</span>
            <span className="text-white font-medium">{stats.estimatedSize}</span>
          </div>
        </div>
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto p-2">
        {sessions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-xs">No chat history yet</p>
          </div>
        ) : (
          <div className="space-y-1">
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className={`w-full text-left p-2 rounded-lg transition-colors group ${
                  session.id === currentSessionId
                    ? 'bg-purple-600/20 border border-purple-500/50'
                    : 'hover:bg-gray-700/50 border border-transparent'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-white truncate font-medium">
                      {session.title}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-500">
                        {session.messages.length} msgs
                      </span>
                      <span className="text-xs text-gray-500">•</span>
                      <span className="text-xs text-gray-500">
                        {formatDate(session.updatedAt)}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDeleteSession(session.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-600/20 rounded transition-all"
                    title="Delete chat"
                  >
                    <Trash2 className="w-3 h-3 text-red-400" />
                  </button>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-3 border-t border-gray-700 space-y-2">
        {/* Export/Import */}
        <div className="flex gap-2">
          <button
            onClick={handleExport}
            disabled={sessions.length === 0}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Export chat history"
          >
            <Download className="w-3 h-3" />
            Export
          </button>
          <label className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs transition-colors cursor-pointer">
            <Upload className="w-3 h-3" />
            Import
            <input
              type="file"
              accept=".json"
              onChange={handleImport}
              className="hidden"
            />
          </label>
        </div>

        {/* Delete All */}
        {sessions.length > 0 && (
          <button
            onClick={handleDeleteAll}
            className={`w-full flex items-center justify-center gap-2 px-3 py-2 rounded text-xs transition-all ${
              showDeleteConfirm
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
            }`}
          >
            <Trash2 className="w-3 h-3" />
            {showDeleteConfirm ? 'Click again to confirm' : 'Delete All'}
          </button>
        )}

        {showDeleteConfirm && (
          <button
            onClick={() => setShowDeleteConfirm(false)}
            className="w-full px-3 py-1 text-xs text-gray-400 hover:text-gray-300 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}
