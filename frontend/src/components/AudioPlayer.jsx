export default function AudioPlayer({ audioUrl }) {
  if (!audioUrl) return null;

  return (
    <div className="w-full">
      <h3 className="text-sm font-medium text-slate-700 mb-2">Generated Audio</h3>
      <audio controls src={audioUrl} className="w-full">
        Your browser does not support the audio element.
      </audio>
    </div>
  );
}
