'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

// Simple text formatter for bot responses
function formatBotMessage(text: string) {
    // Split into lines
    const lines = text.split('\n');
    const elements: JSX.Element[] = [];

    lines.forEach((line, index) => {
        // Bold text (**text**)
        if (line.includes('**')) {
            const parts = line.split('**');
            const formatted = parts.map((part, i) =>
                i % 2 === 1 ? <strong key={i} className="text-purple-300 font-semibold">{part}</strong> : part
            );
            elements.push(<p key={index} className="mb-2">{formatted}</p>);
        }
        // Bullet points
        else if (line.trim().startsWith('-')) {
            elements.push(<li key={index} className="ml-4 text-gray-200">{line.substring(1).trim()}</li>);
        }
        // Emoji lines
        else if (line.trim().match(/^[✅⚠️💡📈🏠🤖]/)) {
            elements.push(<p key={index} className="mb-2 text-lg">{line}</p>);
        }
        // Regular text
        else if (line.trim()) {
            elements.push(<p key={index} className="mb-2">{line}</p>);
        }
    });

    return <div className="space-y-1">{elements}</div>;
}

export default function ChatbotPage() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: `Welcome to Rental Property AI Assistant! 🏠

I can help you with:

1. Demand Forecasting - "What's the demand in Mumbai for August 2024?"
2. Gap Analysis - "Show me investment opportunities in Delhi"
3. Historical Data - "Past trends in Bangalore"

Just ask me anything in natural language!`,
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:5003/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: input }),
            });

            if (!response.ok) {
                throw new Error('Failed to get response');
            }

            const data = await response.json();

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error:', error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please make sure the chatbot API is running on port 5003.',
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const exampleQueries = [
        "What's the demand in Mumbai?",
        "Show me opportunities in Delhi",
        "Historical trends in Bangalore",
    ];

    const handleExampleClick = (query: string) => {
        setInput(query);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
            <div className="container mx-auto px-4 py-8 h-screen flex flex-col">
                {/* Header */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-6 border border-white/20">
                    <h1 className="text-3xl font-bold text-white mb-2">
                        🤖 AI Property Assistant
                    </h1>
                    <p className="text-purple-200">
                        Ask me anything about rental demand, gap analysis, or market trends
                    </p>
                </div>

                {/* Chat Container */}
                <div className="flex-1 bg-white/5 backdrop-blur-lg rounded-2xl border border-white/20 flex flex-col overflow-hidden">
                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-4">
                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'
                                    }`}
                            >
                                <div
                                    className={`max-w-[80%] rounded-2xl px-6 py-4 ${message.role === 'user'
                                            ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                                            : 'bg-white/10 backdrop-blur-md text-white border border-white/20'
                                        }`}
                                >
                                    {message.role === 'assistant' ? (
                                        formatBotMessage(message.content)
                                    ) : (
                                        <p className="whitespace-pre-wrap">{message.content}</p>
                                    )}
                                    <div
                                        className={`text-xs mt-2 ${message.role === 'user'
                                                ? 'text-purple-200'
                                                : 'text-gray-400'
                                            }`}
                                    >
                                        {message.timestamp.toLocaleTimeString()}
                                    </div>
                                </div>
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-white/10 backdrop-blur-md rounded-2xl px-6 py-4 border border-white/20">
                                    <div className="flex space-x-2">
                                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                                        <div
                                            className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"
                                            style={{ animationDelay: '0.1s' }}
                                        ></div>
                                        <div
                                            className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"
                                            style={{ animationDelay: '0.2s' }}
                                        ></div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Example Queries */}
                    {messages.length === 1 && (
                        <div className="px-6 pb-4">
                            <p className="text-sm text-purple-300 mb-2">Try these examples:</p>
                            <div className="flex flex-wrap gap-2">
                                {exampleQueries.map((query, index) => (
                                    <button
                                        key={index}
                                        onClick={() => handleExampleClick(query)}
                                        className="px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-md rounded-full text-sm text-white border border-white/20 transition-all duration-200 hover:scale-105"
                                    >
                                        {query}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Input Area */}
                    <div className="border-t border-white/20 p-6">
                        <div className="flex gap-4">
                            <textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Ask me anything about rental properties..."
                                className="flex-1 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl px-6 py-4 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                                rows={1}
                                disabled={isLoading}
                            />
                            <button
                                onClick={sendMessage}
                                disabled={!input.trim() || isLoading}
                                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-600 text-white rounded-2xl font-semibold transition-all duration-200 hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
                            >
                                {isLoading ? (
                                    <svg
                                        className="animate-spin h-5 w-5"
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                    >
                                        <circle
                                            className="opacity-25"
                                            cx="12"
                                            cy="12"
                                            r="10"
                                            stroke="currentColor"
                                            strokeWidth="4"
                                        ></circle>
                                        <path
                                            className="opacity-75"
                                            fill="currentColor"
                                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                        ></path>
                                    </svg>
                                ) : (
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        strokeWidth={2}
                                        stroke="currentColor"
                                        className="w-5 h-5"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
                                        />
                                    </svg>
                                )}
                            </button>
                        </div>
                        <p className="text-xs text-gray-400 mt-2">
                            Press Enter to send, Shift+Enter for new line
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
