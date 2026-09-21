export default function ErrorMessage({ message }) {
  if (!message) return null;

  return (
    <div className="w-full rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3">
      {message}
    </div>
  );
}
