'use client';

import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, X, Loader2, Volume2, AlertCircle, History, Trash2, Download } from 'lucide-react';
import ChatHistoryPanel from './ChatHistoryPanel';
import {
  createChatSession,
  saveChatSession,
  getChatSession,
  addMessageToSession,
  type ChatMessage,
  type ChatSession,
} from '@/lib/chatHistory';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface VoiceAssistantProps {
  isOpen: boolean;
  onClose: () => void;
  scanResults: any;
}

export default function VoiceAssistant({ isOpen, onClose, scanResults }: VoiceAssistantProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [inputText, setInputText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check if browser supports speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      setSpeechSupported(!!SpeechRecognition);
    }
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Create new session when opened
  useEffect(() => {
    if (isOpen && !currentSessionId) {
      const newSession = createChatSession();
      setCurrentSessionId(newSession.id);

      // Add welcome message
      const welcomeMessage: Message = {
        role: 'assistant',
        content: 'Hello! I\'m your DevAudit AI assistant. Ask me anything about your scan results, like:\n\n• "How do I update my Ethernet controller driver?"\n• "What\'s the biggest security risk right now?"\n• "Explain the BIOS update recommendation"\n• "Should I enable BitLocker?"\n\nYou can speak or type your question.',
        timestamp: new Date(),
      };

      setMessages([welcomeMessage]);

      // Save welcome message to session
      addMessageToSession(newSession.id, welcomeMessage);
    }
  }, [isOpen, currentSessionId]);

  const startListening = () => {
    if (!speechSupported) {
      setError('Speech recognition not supported in this browser. Please use Chrome or Edge, or type your question.');
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInputText(transcript);
      setIsListening(false);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);

      if (event.error === 'no-speech') {
        setError('No speech detected. Please try again.');
      } else if (event.error === 'not-allowed') {
        setError('Microphone access denied. Please enable microphone permissions.');
      } else {
        setError('Speech recognition failed. Please try typing instead.');
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isProcessing || !currentSessionId) return;

    const userMessage: Message = {
      role: 'user',
      content: inputText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsProcessing(true);
    setError(null);

    // Save user message to localStorage
    addMessageToSession(currentSessionId, userMessage);

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputText,
          scan_results: scanResults,
          conversation_history: messages,
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);

        // Save assistant message to localStorage
        addMessageToSession(currentSessionId, assistantMessage);
      } else {
        setError(data.message || 'Failed to get response from AI');
      }
    } catch (err) {
      console.error('AI chat error:', err);
      setError('Failed to connect to AI assistant. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startNewChat = () => {
    const newSession = createChatSession();
    setCurrentSessionId(newSession.id);
    setMessages([]);
    setShowHistory(false);

    // Add welcome message
    const welcomeMessage: Message = {
      role: 'assistant',
      content: 'Hello! I\'m your DevAudit AI assistant. Ask me anything about your scan results.',
      timestamp: new Date(),
    };

    setMessages([welcomeMessage]);
    addMessageToSession(newSession.id, welcomeMessage);
  };

  const loadChatSession = (sessionId: string) => {
    const session = getChatSession(sessionId);
    if (session) {
      setCurrentSessionId(session.id);
      setMessages(session.messages);
      setShowHistory(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className={`bg-gray-900 rounded-lg border border-gray-700 h-[600px] flex ${showHistory ? 'w-full max-w-4xl' : 'w-full max-w-2xl'}`}>
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg">
              <Volume2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">AI Assistant</h2>
              <p className="text-xs text-gray-400">Ask me about your scan results</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={startNewChat}
              className="px-3 py-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
              title="Start new chat"
            >
              New Chat
            </button>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="p-1.5 hover:bg-gray-800 rounded transition-colors"
              title="Chat history"
            >
              <History className="w-5 h-5 text-gray-400" />
            </button>
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-800 rounded transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Privacy Warning */}
        <div className="mx-4 mt-4 p-3 bg-orange-900/20 border border-orange-700/50 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-orange-300">
              <strong>Privacy:</strong> Your questions and scan data are sent to Google Cloud (Vertex AI) for processing.
            </p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-200'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                <p className="text-xs opacity-60 mt-1">
                  {msg.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          {isProcessing && (
            <div className="flex justify-start">
              <div className="bg-gray-800 rounded-lg p-3 flex items-center gap-2">
                <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                <p className="text-sm text-gray-300">Thinking...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="mx-4 mb-2 p-3 bg-red-900/20 border border-red-700/50 rounded-lg">
            <p className="text-xs text-red-300">{error}</p>
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 border-t border-gray-700">
          <div className="flex items-end gap-2">
            {/* Voice Button */}
            <button
              onClick={isListening ? stopListening : startListening}
              disabled={isProcessing || !speechSupported}
              className={`p-3 rounded-lg transition-all duration-200 ${
                isListening
                  ? 'bg-red-600 hover:bg-red-700 animate-pulse'
                  : speechSupported
                  ? 'bg-purple-600 hover:bg-purple-700'
                  : 'bg-gray-700 cursor-not-allowed'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              title={
                !speechSupported
                  ? 'Speech not supported'
                  : isListening
                  ? 'Stop listening'
                  : 'Start voice input'
              }
            >
              {isListening ? (
                <MicOff className="w-5 h-5 text-white" />
              ) : (
                <Mic className="w-5 h-5 text-white" />
              )}
            </button>

            {/* Text Input */}
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question... (or use voice)"
              disabled={isProcessing || isListening}
              className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-3 resize-none border border-gray-700 focus:border-blue-600 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
              rows={2}
            />

            {/* Send Button */}
            <button
              onClick={sendMessage}
              disabled={!inputText.trim() || isProcessing || isListening}
              className="p-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5 text-white" />
            </button>
          </div>

          {!speechSupported && (
            <p className="text-xs text-gray-500 mt-2">
              Voice input not supported. Use Chrome or Edge for voice features.
            </p>
          )}
        </div>
        </div>

        {/* Chat History Sidebar */}
        {showHistory && (
          <ChatHistoryPanel
            currentSessionId={currentSessionId}
            onSelectSession={loadChatSession}
            onClose={() => setShowHistory(false)}
          />
        )}
      </div>
    </div>
  );
}
