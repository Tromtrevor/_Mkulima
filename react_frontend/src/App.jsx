import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <div className="min-h-screen bg-[#f7f8f5] md:flex">
      <Sidebar />

      <div className="min-w-0 flex-1">
        <Navbar />

        <main className="mx-auto max-w-[1600px] p-4 md:p-8">
          <Dashboard />
        </main>
      </div>
    </div>
  );
}