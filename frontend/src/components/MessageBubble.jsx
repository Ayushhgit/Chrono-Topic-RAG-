export default function MessageBubble({ role, content }) {
  const isUser = role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end mb-6 anim-in">
        <div className="max-w-[75%] px-5 py-2.5 rounded-[22px] text-[15px] leading-7 bg-[#2f2f2f] text-[#ececec]">
          {content}
        </div>
      </div>
    );
  }

  // Assistant rendering
  const renderLine = (line, i) => {
    // Bold
    let html = line.replace(/\*\*(.+?)\*\*/g, '<strong style="font-weight:600;color:#ececec">$1</strong>');
    
    // List item
    if (/^\s*[-•]\s/.test(line)) {
      const text = line.replace(/^\s*[-•]\s*/, '');
      const processed = text.replace(/\*\*(.+?)\*\*/g, '<strong style="font-weight:600;color:#ececec">$1</strong>');
      return (
        <li key={i} className="ml-6 mb-1.5 list-disc pl-1 text-[15px] leading-7">
          <span dangerouslySetInnerHTML={{ __html: processed }} />
        </li>
      );
    }

    if (!line.trim()) return <div key={i} className="h-4" />;

    return (
      <p key={i} className="mb-4 last:mb-0 text-[15px] leading-7">
        {html.includes('<strong') ? (
          <span dangerouslySetInnerHTML={{ __html: html }} />
        ) : (
          line
        )}
      </p>
    );
  };

  return (
    <div className="flex mb-6 anim-in">
      <div className="flex-shrink-0 w-8 h-8 rounded-full border border-[#424242] flex items-center justify-center mr-4 mt-0.5 bg-[#212121]">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ececec" strokeWidth="1.5">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
        </svg>
      </div>
      <div className="flex-1 min-w-0 text-[#d1d5db]">
        {content.split('\n').map(renderLine)}
      </div>
    </div>
  );
}
