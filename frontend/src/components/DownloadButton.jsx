export default function DownloadButton({ audioUrl }) {
  if (!audioUrl) return null;

  return (
    <a
      href={audioUrl}
      download
      className="inline-block px-5 py-2 rounded-lg border border-indigo-600 text-indigo-600 font-medium hover:bg-indigo-50 transition"
    >
      Download Audio
    </a>
  );
}
