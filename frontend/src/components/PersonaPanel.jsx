export default function PersonaPanel({ persona }) {
  if (!persona) {
    return <div className="px-3 py-4 text-[13px] text-[#6b6b6b]">Upload a CSV first</div>;
  }

  const sections = [
    { key: 'habits', label: 'Habits & Routines' },
    { key: 'personal_facts', label: 'Personal Facts' },
    { key: 'personality_traits', label: 'Personality' },
    { key: 'communication_style', label: 'Communication' },
  ];

  return (
    <div className="flex flex-col w-full">
      {sections.map(({ key, label }) => {
        const items = persona[key] || [];
        if (!items.length) return null;
        return (
          <div key={key} className="mb-6 w-full">
            <div className="px-3 py-1 text-[12px] font-semibold text-[#6b6b6b] mb-1">{label}</div>
            <div className="flex flex-col w-full gap-1">
              {items.map((item, i) => (
                <div key={i} className="px-3 py-2 text-[13px] leading-snug text-[#ececec] rounded-lg hover:bg-[#212121] transition-colors cursor-pointer break-words">
                  {item}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
