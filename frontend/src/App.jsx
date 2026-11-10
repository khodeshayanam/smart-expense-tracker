import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Expenses from "./pages/Expenses";
import Habits from "./pages/Habits";
import Categories from "./pages/Categories";
import AIInsights from "./pages/AIInsights";

export default function App() {
  return (
    <div className="flex min-h-screen bg-bg">
      <Sidebar />
      <main className="flex-1 p-6 lg:p-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/expenses" element={<Expenses />} />
          <Route path="/habits" element={<Habits />} />
          <Route path="/categories" element={<Categories />} />
          <Route path="/ai" element={<AIInsights />} />
        </Routes>
      </main>
    </div>
  );
}
