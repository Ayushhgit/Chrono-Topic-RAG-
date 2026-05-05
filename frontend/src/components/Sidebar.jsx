import { useState } from 'react';
import PersonaPanel from './PersonaPanel';
import TopicsPanel from './TopicsPanel';

export default function Sidebar({ persona, topics, isOpen, onToggle, onUpload }) {
  const [tab, setTab] = useState('persona');
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState('');
  const [dragOver, setDragOver] = useState(false);

  const handleFile = async (e) => {
    const file = e.target.files?.[0] || e.dataTransfer?.files?.[0];
    if (!file) return;
    
    setUploading(true);
    setUploadMsg('');
    
    try {
      const r = await onUpload(file);
      setUploadMsg(`${r.total_messages.toLocaleString()} messages · ${r.total_topics} topics`);
    } catch (err) {
      setUploadMsg('Upload failed — try again');
    } finally {
      setUploading(false);
      setDragOver(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFile(e);
  };

  // Collapsed state
  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className="absolute top-4 left-4 z-50 p-2.5 rounded-xl bg-[#1a1a1a] border border-[#2a2a2a] 
                   text-[#a0a0a0] hover:text-[#ececec] hover:border-[#3a3a3a] hover:bg-[#222] 
                   transition-all duration-200 shadow-lg hover:shadow-xl"
        title="Open sidebar"
      >
        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" viewBox="0 0 24 24">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <path d="M9 3v18"/>
        </svg>
      </button>
    );
  }

  return (
    <aside 
      className="flex-shrink-0 flex flex-col h-full bg-[#0f0f0f] border-r border-[#262626] 
                 w-[280px] overflow-hidden shadow-2xl"
    >
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3.5 border-b border-[#1f1f1f]">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 
                          flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <svg width="14" height="14" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" viewBox="0 0 24 24">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
          <span className="text-[13px] font-semibold text-[#ececec] tracking-tight">Analysis</span>
        </div>
        
        <div className="flex items-center gap-1">
          <button
            onClick={onToggle}
            className="p-1.5 rounded-lg text-[#666] hover:text-[#ececec] hover:bg-[#1f1f1f] 
                       transition-all duration-150"
            title="Collapse sidebar"
          >
            <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" viewBox="0 0 24 24">
              <rect x="3" y="3" width="18" height="18" rx="2"/>
              <path d="M9 3v18"/>
            </svg>
          </button>
        </div>
      </header>

      {/* Upload Zone */}
      <div className="px-3 pt-3 pb-2">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            relative group cursor-pointer rounded-xl border-2 border-dashed 
            transition-all duration-200 overflow-hidden
            ${dragOver 
              ? 'border-indigo-500/60 bg-indigo-500/5' 
              : 'border-[#2a2a2a] hover:border-[#3a3a3a] bg-[#141414] hover:bg-[#181818]'
            }
          `}
        >
          <label className="flex flex-col items-center gap-2 py-4 px-4 cursor-pointer">
            <div className={`
              w-9 h-9 rounded-full flex items-center justify-center transition-all duration-200
              ${dragOver 
                ? 'bg-indigo-500/20 text-indigo-400' 
                : 'bg-[#1f1f1f] text-[#555] group-hover:text-[#888] group-hover:bg-[#252525]'
              }
            `}>
              {uploading ? (
                <svg className="animate-spin" width="18" height="18" fill="none" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeDasharray="60" strokeDashoffset="20"/>
                </svg>
              ) : (
                <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" viewBox="0 0 24 24">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
              )}
            </div>
            
            <div className="text-center">
              <p className="text-[12px] font-medium text-[#999] group-hover:text-[#bbb] transition-colors">
                {uploading ? 'Processing...' : dragOver ? 'Drop CSV here' : 'Upload CSV'}
              </p>
              <p className="text-[10px] text-[#444] mt-0.5">Drag & drop or click to browse</p>
            </div>
            
            <input 
              type="file" 
              accept=".csv" 
              onChange={handleFile} 
              className="hidden" 
              disabled={uploading}
            />
          </label>
        </div>

        {/* Upload Status */}
        {uploadMsg && (
          <div className={`
            mt-2 px-3 py-2 rounded-lg text-[11px] font-medium flex items-center gap-2
            ${uploadMsg.includes('failed') 
              ? 'bg-red-500/10 text-red-400 border border-red-500/20' 
              : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
            }
          `}>
            <div className={`w-1.5 h-1.5 rounded-full ${uploadMsg.includes('failed') ? 'bg-red-400' : 'bg-emerald-400'}`}/>
            {uploadMsg}
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <nav className="px-3 pb-1">
        <div className="flex gap-1 p-1 bg-[#141414] rounded-xl border border-[#1f1f1f]">
          <button
            onClick={() => setTab('persona')}
            className={`
              flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-[12px] font-semibold
              transition-all duration-200
              ${tab === 'persona'
                ? 'bg-[#1f1f1f] text-[#ececec] shadow-sm'
                : 'text-[#666] hover:text-[#999] hover:bg-[#1a1a1a]'
              }
            `}
          >
            <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" viewBox="0 0 24 24">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            Persona
          </button>
          
          <button
            onClick={() => setTab('topics')}
            className={`
              flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-[12px] font-semibold
              transition-all duration-200
              ${tab === 'topics'
                ? 'bg-[#1f1f1f] text-[#ececec] shadow-sm'
                : 'text-[#666] hover:text-[#999] hover:bg-[#1a1a1a]'
              }
            `}
          >
            <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" viewBox="0 0 24 24">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            Topics
          </button>
        </div>
      </nav>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto px-3 pt-3 pb-6">
        {/* Section Label */}
        <div className="flex items-center gap-2 px-1 mb-3">
          <div className="h-px flex-1 bg-gradient-to-r from-[#2a2a2a] to-transparent"/>
          <span className="text-[10px] font-bold text-[#444] uppercase tracking-[0.15em]">
            {tab === 'persona' ? 'Persona Profile' : 'Topic Clusters'}
          </span>
          <div className="h-px flex-1 bg-gradient-to-l from-[#2a2a2a] to-transparent"/>
        </div>

        {/* Panel Content */}
        <div className="bg-[#141414] rounded-xl border border-[#1f1f1f] overflow-hidden">
          {tab === 'persona' 
            ? <PersonaPanel persona={persona}/> 
            : <TopicsPanel topics={topics}/>
          }
        </div>
      </div>

      {/* Footer */}
      <footer className="px-4 py-3 border-t border-[#1f1f1f] bg-[#0c0c0c]">
        <div className="flex items-center justify-between text-[10px] text-[#333]">
          <span>v1.0</span>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/50 animate-pulse"/>
            <span>Ready</span>
          </div>
        </div>
      </footer>
    </aside>
  );
}