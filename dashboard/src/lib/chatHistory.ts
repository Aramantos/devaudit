/**
 * Chat History Management
 *
 * Stores voice assistant conversations locally in browser localStorage.
 * All chat data stays on your machine - nothing is sent to any server.
 */

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
}

const STORAGE_KEY = 'devaudit_chat_history';
const MAX_SESSIONS = 50; // Limit to prevent localStorage overflow

/**
 * Generate a unique session ID
 */
function generateSessionId(): string {
  return `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Generate a title from the first user message
 */
function generateTitle(firstMessage: string): string {
  const maxLength = 50;
  const cleaned = firstMessage.trim();

  if (cleaned.length <= maxLength) {
    return cleaned;
  }

  return cleaned.substring(0, maxLength - 3) + '...';
}

/**
 * Get all chat sessions from localStorage
 */
export function getChatSessions(): ChatSession[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];

    const sessions = JSON.parse(stored);

    // Convert date strings back to Date objects
    return sessions.map((session: any) => ({
      ...session,
      createdAt: new Date(session.createdAt),
      updatedAt: new Date(session.updatedAt),
      messages: session.messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      })),
    }));
  } catch (error) {
    console.error('Failed to load chat history:', error);
    return [];
  }
}

/**
 * Save chat sessions to localStorage
 */
function saveChatSessions(sessions: ChatSession[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
  } catch (error) {
    console.error('Failed to save chat history:', error);

    // If localStorage is full, remove oldest session and retry
    if (error instanceof DOMException && error.name === 'QuotaExceededError') {
      const sortedSessions = [...sessions].sort(
        (a, b) => a.updatedAt.getTime() - b.updatedAt.getTime()
      );
      sortedSessions.shift(); // Remove oldest
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sortedSessions));
    }
  }
}

/**
 * Create a new chat session
 */
export function createChatSession(firstUserMessage?: string): ChatSession {
  const session: ChatSession = {
    id: generateSessionId(),
    title: firstUserMessage ? generateTitle(firstUserMessage) : 'New Chat',
    messages: [],
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  return session;
}

/**
 * Get a specific chat session by ID
 */
export function getChatSession(sessionId: string): ChatSession | null {
  const sessions = getChatSessions();
  return sessions.find(s => s.id === sessionId) || null;
}

/**
 * Save or update a chat session
 */
export function saveChatSession(session: ChatSession): void {
  const sessions = getChatSessions();
  const existingIndex = sessions.findIndex(s => s.id === session.id);

  // Update timestamp
  session.updatedAt = new Date();

  if (existingIndex >= 0) {
    // Update existing session
    sessions[existingIndex] = session;
  } else {
    // Add new session
    sessions.push(session);

    // Enforce max sessions limit
    if (sessions.length > MAX_SESSIONS) {
      const sortedSessions = sessions.sort(
        (a, b) => a.updatedAt.getTime() - b.updatedAt.getTime()
      );
      sortedSessions.shift(); // Remove oldest
      saveChatSessions(sortedSessions);
      return;
    }
  }

  saveChatSessions(sessions);
}

/**
 * Add a message to a chat session
 */
export function addMessageToSession(
  sessionId: string,
  message: ChatMessage
): ChatSession | null {
  const session = getChatSession(sessionId);
  if (!session) return null;

  session.messages.push(message);

  // Update title if this is the first user message
  if (session.messages.length === 1 && message.role === 'user') {
    session.title = generateTitle(message.content);
  }

  saveChatSession(session);
  return session;
}

/**
 * Delete a specific chat session
 */
export function deleteChatSession(sessionId: string): void {
  const sessions = getChatSessions();
  const filtered = sessions.filter(s => s.id !== sessionId);
  saveChatSessions(filtered);
}

/**
 * Delete all chat sessions
 */
export function deleteAllChatSessions(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to delete chat history:', error);
  }
}

/**
 * Get storage usage statistics
 */
export function getChatStorageStats(): {
  sessionCount: number;
  totalMessages: number;
  estimatedSize: string;
} {
  const sessions = getChatSessions();
  const totalMessages = sessions.reduce((sum, s) => sum + s.messages.length, 0);

  // Estimate size in KB
  const stored = localStorage.getItem(STORAGE_KEY) || '';
  const sizeKB = (stored.length * 2) / 1024; // UTF-16 uses 2 bytes per char

  return {
    sessionCount: sessions.length,
    totalMessages,
    estimatedSize: `${sizeKB.toFixed(2)} KB`,
  };
}

/**
 * Export chat history as JSON
 */
export function exportChatHistory(): string {
  const sessions = getChatSessions();
  return JSON.stringify(sessions, null, 2);
}

/**
 * Import chat history from JSON
 */
export function importChatHistory(jsonData: string): boolean {
  try {
    const sessions = JSON.parse(jsonData);

    // Validate structure
    if (!Array.isArray(sessions)) {
      throw new Error('Invalid format: expected array of sessions');
    }

    // Convert date strings to Date objects
    const validatedSessions = sessions.map((session: any) => ({
      ...session,
      createdAt: new Date(session.createdAt),
      updatedAt: new Date(session.updatedAt),
      messages: session.messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      })),
    }));

    saveChatSessions(validatedSessions);
    return true;
  } catch (error) {
    console.error('Failed to import chat history:', error);
    return false;
  }
}
