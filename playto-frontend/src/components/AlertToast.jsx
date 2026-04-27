export default function AlertToast({ message, type }) {
  return (
    <div className={`fixed top-5 right-5 p-4 rounded shadow text-white
      ${type === "error" ? "bg-red-500" : "bg-green-500"}`}>
      {message}
    </div>
  );
}