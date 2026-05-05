import { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import { sendChatMessage, fetchPersona, fetchTopics, fetchHealth, uploadCSV } from './api';

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [persona, setPersona] = useState(null);
  const [topics, setTopics] = useState([]);
  const [backendReady, setBackendReady] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const h = await fetchHealth();
        setBackendReady(true);
        if (h.processed) loadData();
      } catch { setBackendReady(false); }
    })();
  }, []);

  const loadData = async () => {
    try {
      const [p, t] = await Promise.all([fetchPersona(), fetchTopics()]);
      setPersona(p);
      setTopics(t);
    } catch {}
  };

  const handleSend = useCallback(async (query) => {
    setMessages(p => [...p, { role: 'user', content: query }]);
    setIsLoading(true);
    try {
      const d = await sendChatMessage(query);
      setMessages(p => [...p, { role: 'assistant', content: d.response }]);
    } catch (e) {
      setMessages(p => [...p, { role: 'assistant', content: `Error: ${e.message}` }]);
    } finally { setIsLoading(false); }
  }, []);

  const handleUpload = useCallback(async (file) => {
    const r = await uploadCSV(file);
    await loadData();
    return r;
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#212121] text-[#ececec]">
      {/* Sidebar - using flex layout instead of fixed to prevent overlap */}
      <Sidebar
        persona={persona}
        topics={topics}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(o => !o)}
        onUpload={handleUpload}
      />
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full relative">
        {!backendReady && (
          <div className="px-4 py-2 text-center text-[12px] text-red-400 bg-[#1a1212] border-b border-[#2a1515]">
            Backend not connected. Start FastAPI on port 8000.
          </div>
        )}
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onSend={handleSend}
          sidebarOpen={sidebarOpen}
        />
      </div>
    </div>
  );
}
