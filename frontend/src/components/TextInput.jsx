export default function TextInput({ value, onChange, maxLength = 5000 }) {
  const charCount = value.length;
  const wordCount = value.trim() === "" ? 0 : value.trim().split(/\s+/).length;
  const overLimit = charCount > maxLength;

  return (
    <div className="w-full">
      <label htmlFor="tts-text" className="block text-sm font-medium text-slate-700 mb-1">
        Enter your text
      </label>
      <textarea
        id="tts-text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={6}
        placeholder="Type or paste the text you want converted to speech..."
        className={`w-full rounded-lg border p-3 text-slate-800 focus:outline-none focus:ring-2 ${
          overLimit
            ? "border-red-400 focus:ring-red-300"
            : "border-slate-300 focus:ring-indigo-300"
        }`}
      />
      <div className="flex justify-between text-xs mt-1 text-slate-500">
        <span>{wordCount} words</span>
        <span className={overLimit ? "text-red-500 font-medium" : ""}>
          {charCount} / {maxLength} characters
        </span>
      </div>
    </div>
  );
}
