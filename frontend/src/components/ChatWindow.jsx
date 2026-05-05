import { useState, useRef, useEffect, useCallback } from 'react';

// ─── Utility Components ───────────────────────────────────────────

const Avatar = ({ size = 32, className = "" }) => (
  <div className={`rounded-full border border-[#333] bg-gradient-to-br from-[#1a1a1a] to-[#0f0f0f] 
                  flex items-center justify-center shadow-lg shadow-black/20 ${className}`}
       style={{ width: size, height: size }}>
    <svg width={size * 0.5} height={size * 0.5} viewBox="0 0 24 24" fill="none" 
         stroke="#a0a0a0" strokeWidth="1.5" strokeLinecap="round">
      <path d="M12 2L2 7l10 5 10-5-10-5z"/>
      <path d="M2 17l10 5 10-5"/>
      <path d="M2 12l10 5 10-5"/>
    </svg>
  </div>
);

const ThinkingDots = () => (
  <div className="flex items-center gap-1.5 h-8 px-1">
    {[0, 1, 2].map(i => (
      <span key={i} 
            className="w-2 h-2 rounded-full bg-[#555] animate-bounce"
            style={{ animationDelay: `${i * 0.15}s`, animationDuration: '1.2s' }}/>
    ))}
  </div>
);

const SendIcon = ({ active }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" 
       stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
       className={`transition-transform duration-200`}>
    <path d="M12 19V5M5 12l7-7 7 7"/>
  </svg>
);

const SparkleIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" 
       stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M12 3L14.5 8.5L20 9L16 13L17.5 18.5L12 16L6.5 18.5L8 13L4 9L9.5 8.5L12 3Z"/>
  </svg>
);

// ─── Main Component ────────────────────────────────────────────────

export default function ChatWindow({ messages, isLoading, onSend, sidebarOpen = true }) {
  const [input, setInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [hoveredSuggestion, setHoveredSuggestion] = useState(null);
  const endRef = useRef(null);
  const taRef = useRef(null);
  const containerRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, isLoading]);

  // Auto-resize textarea
  useEffect(() => {
    if (taRef.current) {
      taRef.current.style.height = 'auto';
      const newHeight = Math.min(taRef.current.scrollHeight, 240);
      taRef.current.style.height = newHeight + 'px';
    }
  }, [input]);

  const send = useCallback(() => {
    if (!input.trim() || isLoading) return;
    onSend(input.trim());
    setInput('');
    if (taRef.current) taRef.current.style.height = 'auto';
  }, [input, isLoading, onSend]);

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const hasMessages = messages.length > 0 || isLoading;

  // ─── Markdown-ish Renderer ───────────────────────────────────────
  const renderAssistantMessage = (content) => {
    const lines = content.split('\n');
    const elements = [];
    let inList = false;
    let listItems = [];

    const flushList = () => {
      if (listItems.length > 0) {
        elements.push(
          <ul key={`list-${elements.length}`} className="space-y-1.5 my-3 ml-1">
            {listItems.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-[15px] leading-relaxed text-[#d0d0d0]">
                <span className="mt-2.5 w-1 h-1 rounded-full bg-[#555] flex-shrink-0"/>
                <span dangerouslySetInnerHTML={{ 
                  __html: item.replace(/\*\*(.+?)\*\*/g, '<strong class="text-[#ececec] font-semibold">$1</strong>') 
                }}/>
              </li>
            ))}
          </ul>
        );
        listItems = [];
        inList = false;
      }
    };

    lines.forEach((line, i) => {
      const trimmed = line.trim();
      
      // Empty line
      if (!trimmed) {
        flushList();
        elements.push(<div key={`spacer-${i}`} className="h-3"/>);
        return;
      }

      // List item
      if (/^[-•*]\s/.test(trimmed)) {
        inList = true;
        listItems.push(trimmed.replace(/^[-•*]\s*/, ''));
        return;
      }

      // Flush list if we hit non-list content
      flushList();

      // Heading
      if (/^#{1,3}\s/.test(trimmed)) {
        const level = trimmed.match(/^#+/)[0].length;
        const text = trimmed.replace(/^#+\s*/, '');
        const sizes = { 1: 'text-xl', 2: 'text-lg', 3: 'text-base' };
        elements.push(
          <h3 key={`h-${i}`} className={`${sizes[level]} font-bold text-[#ececec] mt-4 mb-2 tracking-tight`}>
            {text}
          </h3>
        );
        return;
      }

      // Regular paragraph
      const processed = trimmed
        .replace(/\*\*(.+?)\*\*/g, '<strong class="text-[#ececec] font-semibold">$1</strong>')
        .replace(/`(.+?)`/g, '<code class="px-1.5 py-0.5 rounded-md bg-[#2a2a2a] text-[#b0b0b0] text-[13px] font-mono border border-[#333]">$1</code>');
      
      elements.push(
        <p key={`p-${i}`} className="text-[15px] leading-[1.7] text-[#d0d0d0] my-1"
           dangerouslySetInnerHTML={{ __html: processed }}/>
      );
    });

    flushList();
    return elements;
  };

  // ─── Suggestion Cards Data ─────────────────────────────────────
  const suggestions = [
    { 
      icon: '👤', 
      title: 'Explain persona', 
      desc: 'What kind of person is this user?',
      prompt: 'Explain what kind of person this user is based on their conversations'
    },
    { 
      icon: '📊', 
      title: 'Summarize habits', 
      desc: 'Daily routines & patterns',
      prompt: 'Summarize their daily habits and routines'
    },
    { 
      icon: '💬', 
      title: 'Analyze tone', 
      desc: 'Communication style insights',
      prompt: 'Analyze how they communicate'
    },
    { 
      icon: '🏷️', 
      title: 'List topics', 
      desc: 'Main discussion themes',
      prompt: 'List the main topics discussed'
    },
  ];

  // ─── Render ──────────────────────────────────────────────────────
  return (
    <div className="flex flex-col h-full bg-[#0a0a0a] relative w-full overflow-hidden">
      
      {/* ═══ Subtle Background Texture ═══ */}
      <div className="absolute inset-0 opacity-[0.02] pointer-events-none"
           style={{
             backgroundImage: `radial-gradient(circle at 1px 1px, #fff 1px, transparent 0)`,
             backgroundSize: '32px 32px'
           }}/>

      {/* ═══ Header ═══ */}
      <header className={`sticky top-0 z-20 flex items-center justify-between pr-6 py-3.5 
                         bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-[#1a1a1a] transition-all duration-300
                         ${!sidebarOpen ? 'pl-[72px]' : 'pl-6'}`}>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500/20 to-purple-500/20 
                          border border-indigo-500/20 flex items-center justify-center">
            <SparkleIcon/>
          </div>
          <div className="flex flex-col">
            <span className="text-[14px] font-semibold text-[#ececec] tracking-tight leading-none">
              ConvoLens
            </span>
            <span className="text-[10px] text-[#444] mt-0.5 font-medium tracking-wide uppercase">
              AI Conversation Analyst
            </span>
          </div>
        </div>
        
        {hasMessages && (
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#111] border border-[#222]">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"/>
              <span className="text-[10px] text-[#555] font-medium uppercase tracking-wider">
                {messages.length} msgs
              </span>
            </div>
          </div>
        )}
      </header>

      {/* ═══ Main Content Area ═══ */}
      <div ref={containerRef} className="flex-1 overflow-y-auto w-full flex flex-col relative">
        
        {/* ── Empty State ── */}
        {!hasMessages ? (
          <div className="flex-1 flex flex-col items-center justify-center px-4 text-center min-h-0">
            
            {/* Animated Logo Orb */}
            <div className="relative mb-10 group">
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-pink-500/20 
                              rounded-full blur-2xl opacity-60 group-hover:opacity-80 transition-opacity duration-700"/>
              <div className="relative w-20 h-20 rounded-2xl bg-gradient-to-br from-[#1a1a1a] to-[#0f0f0f] 
                              border border-[#2a2a2a] flex items-center justify-center shadow-2xl
                              group-hover:border-[#3a3a3a] transition-all duration-500">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" 
                     stroke="url(#logoGradient)" strokeWidth="1.2" strokeLinecap="round">
                  <defs>
                    <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#6366f1"/>
                      <stop offset="100%" stopColor="#a855f7"/>
                    </linearGradient>
                  </defs>
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
              </div>
            </div>

            {/* Headline */}
            <h1 className="text-[32px] font-bold text-[#ececec] mb-3 tracking-tight leading-tight">
              What can I help with?
            </h1>
            <p className="text-[14px] text-[#555] mb-10 max-w-md leading-relaxed">
              Upload a conversation CSV and ask anything about the user's personality, 
              habits, communication style, or discussion topics.
            </p>

            {/* Suggestion Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-[560px] w-full">
              {suggestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => onSend(q.prompt)}
                  onMouseEnter={() => setHoveredSuggestion(i)}
                  onMouseLeave={() => setHoveredSuggestion(null)}
                  className={`group relative flex flex-col p-4 rounded-2xl border text-left 
                              transition-all duration-300 overflow-hidden
                              ${hoveredSuggestion === i 
                                ? 'bg-[#141414] border-[#333] shadow-lg shadow-black/20 scale-[1.02]' 
                                : 'bg-[#0f0f0f] border-[#1f1f1f] hover:bg-[#111] hover:border-[#2a2a2a]'
                              }`}
                >
                  {/* Hover glow */}
                  <div className={`absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 
                                   transition-opacity duration-300 ${hoveredSuggestion === i ? 'opacity-100' : 'opacity-0'}`}/>
                  
                  <div className="relative">
                    <span className="text-xl mb-2 block">{q.icon}</span>
                    <span className="text-[13px] font-semibold text-[#ececec] block mb-1">{q.title}</span>
                    <span className="text-[12px] text-[#555] leading-relaxed">{q.desc}</span>
                  </div>
                  
                  <div className={`absolute bottom-3 right-3 transition-all duration-300
                                  ${hoveredSuggestion === i ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-2'}`}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#666" strokeWidth="2">
                      <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          
          /* ── Message Thread ── */
          <div className="w-full flex-1 flex justify-center">
            <div className="w-full max-w-[760px] px-4 pt-6 pb-4">
              
              {/* Date separator for first message */}
              <div className="flex items-center gap-3 mb-8">
                <div className="h-px flex-1 bg-gradient-to-r from-transparent via-[#222] to-transparent"/>
                <span className="text-[10px] font-bold text-[#333] uppercase tracking-[0.2em]">
                  Conversation
                </span>
                <div className="h-px flex-1 bg-gradient-to-r from-transparent via-[#222] to-transparent"/>
              </div>

              {messages.map((m, i) => (
                <div key={i} className="mb-8 animate-fade-in">
                  
                  {/* USER MESSAGE */}
                  {m.role === 'user' ? (
                    <div className="flex justify-end group/message">
                      <div className="max-w-[85%] relative">
                        {/* Subtle gradient border effect */}
                        <div className="absolute -inset-[1px] bg-gradient-to-r from-indigo-500/10 to-purple-500/10 
                                        rounded-[20px] opacity-0 group-hover/message:opacity-100 transition-opacity duration-300"/>
                        <div className="relative px-5 py-3.5 rounded-[20px] bg-[#1a1a1a] border border-[#2a2a2a] 
                                        text-[#ececec] text-[15px] leading-[1.6] shadow-sm">
                          {m.content}
                        </div>
                        <div className="text-right mt-1.5 mr-2">
                          <span className="text-[10px] text-[#333] font-medium">You</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    
                    /* ASSISTANT MESSAGE */
                    <div className="flex gap-4 group/message">
                      <div className="flex-shrink-0 pt-1">
                        <Avatar size={28}/>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-[11px] font-semibold text-[#555] uppercase tracking-wider">
                            ConvoLens
                          </span>
                          <div className="w-1 h-1 rounded-full bg-[#333]"/>
                          <span className="text-[10px] text-[#333]">AI</span>
                        </div>
                        <div className="text-[15px] leading-[1.7] text-[#c0c0c0]">
                          {renderAssistantMessage(m.content)}
                        </div>
                        
                        {/* Action bar on hover */}
                        <div className="flex items-center gap-1 mt-3 opacity-0 group-hover/message:opacity-100 
                                        transition-opacity duration-200">
                          <button className="p-1.5 rounded-lg hover:bg-[#1a1a1a] text-[#444] hover:text-[#666] 
                                           transition-colors" title="Copy">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                            </svg>
                          </button>
                          <button className="p-1.5 rounded-lg hover:bg-[#1a1a1a] text-[#444] hover:text-[#666] 
                                           transition-colors" title="Regenerate">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              {/* Loading State */}
              {isLoading && (
                <div className="flex gap-4 mb-8 animate-fade-in">
                  <div className="flex-shrink-0 pt-1">
                    <Avatar size={28}/>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-[11px] font-semibold text-[#555] uppercase tracking-wider">
                        ConvoLens
                      </span>
                      <div className="w-1 h-1 rounded-full bg-[#333]"/>
                      <span className="text-[10px] text-[#333]">Thinking...</span>
                    </div>
                    <div className="bg-[#111] border border-[#1a1a1a] rounded-2xl px-4 py-3 inline-flex">
                      <ThinkingDots/>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={endRef} className="h-24" />
            </div>
          </div>
        )}
      </div>

      {/* ═══ Input Area ═══ */}
      <div className="relative z-10 w-full flex justify-center">
        {/* Gradient fade above input */}
        <div className="absolute bottom-full left-0 right-0 h-16 bg-gradient-to-t from-[#0a0a0a] to-transparent 
                        pointer-events-none"/>
        
        <div className="w-full max-w-[760px] px-6 md:px-8 pb-8 pt-2">
          <div className={`
            flex items-end w-full rounded-xl bg-[#141414] py-3.5 px-3.5 
            border transition-all duration-300 shadow-2xl shadow-black/30
            ${isFocused 
              ? 'border-[#444] shadow-indigo-500/10 ring-1 ring-indigo-500/20' 
              : 'border-[#2a2a2a] hover:border-[#3a3a3a]'
            }
          `}>
            {/* Textarea */}
            <textarea
              ref={taRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={onKey}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="Ask about the conversation..."
              disabled={isLoading}
              rows={1}
              className="flex-1 bg-transparent text-[#ececec] placeholder-[#555] text-[16px] 
                         leading-[24px] py-[10px] px-3 resize-none outline-none min-h-[44px]"
              style={{ maxHeight: '240px' }}
            />
            
            {/* Send Button */}
            <button
              onClick={send}
              disabled={isLoading || !input.trim()}
              className={`
                flex-shrink-0 w-[34px] h-[34px] rounded-xl flex items-center justify-center mb-[5px] ml-2
                transition-all duration-200
                ${input.trim() 
                  ? 'bg-white text-black hover:bg-[#e0e0e0] hover:scale-105 active:scale-95 shadow-lg shadow-white/10' 
                  : 'bg-[#222] text-[#555] cursor-not-allowed border border-[#333]'
                }
              `}
            >
              <SendIcon active={!!input.trim()}/>
            </button>
          </div>
          
          {/* Footer text */}
          <div className="flex items-center justify-center gap-2 mt-3">
            <div className="w-1 h-1 rounded-full bg-[#222]"/>
            <p className="text-[11px] text-center text-[#333] font-medium">
              ConvoLens runs locally. Responses are based on uploaded conversation data only.
            </p>
            <div className="w-1 h-1 rounded-full bg-[#222]"/>
          </div>
        </div>
      </div>

      {/* ═══ Global Styles for Animations ═══ */}
      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
      `}</style>
    </div>
  );
}