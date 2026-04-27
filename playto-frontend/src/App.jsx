import Sidebar from "./components/Sidebar";
import AppRoutes from "./routes/AppRoutes";

export default function App() {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 bg-gray-100 min-h-screen">
        <AppRoutes />
      </div>
    </div>
  );
}