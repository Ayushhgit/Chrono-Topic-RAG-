export default function TopicsPanel({ topics }) {
  if (!topics || !topics.length) {
    return <div className="px-3 py-4 text-[13px] text-[#6b6b6b]">Upload a CSV first</div>;
  }

  return (
    <div className="flex flex-col w-full gap-2">
      {topics.map(t => (
        <div key={t.topic_id} className="group relative px-3 py-3 w-full text-[13px] text-[#ececec] rounded-lg hover:bg-[#212121] transition-colors cursor-pointer">
          <div className="flex items-center justify-between mb-1">
            <span className="font-semibold text-[13px]">Topic {t.topic_id}</span>
            <span className="text-[11px] text-[#6b6b6b]">#{t.start_index}-{t.end_index}</span>
          </div>
          <div className="text-[12px] text-[#9b9b9b] leading-snug line-clamp-3">
            {t.summary || `Topic ${t.topic_id}`}
          </div>
        </div>
      ))}
    </div>
  );
}
