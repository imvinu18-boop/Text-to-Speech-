export default function VoiceSelector({ voices, value, onChange, loading }) {
  return (
    <div>
      <label htmlFor="voice" className="block text-sm font-medium text-slate-700 mb-1">
        Voice / Accent
      </label>
      <select
        id="voice"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={loading || voices.length === 0}
        className="w-full rounded-lg border border-slate-300 p-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-300 disabled:bg-slate-100 disabled:text-slate-400"
      >
        {loading && <option>Loading voices...</option>}
        {!loading && voices.length === 0 && <option>No voices available</option>}
        {!loading &&
          voices.map((voice) => (
            <option key={voice.name} value={voice.name}>
              {voice.label}
            </option>
          ))}
      </select>
    </div>
  );
}
