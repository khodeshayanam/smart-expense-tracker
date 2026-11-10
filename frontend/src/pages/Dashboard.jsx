import { useEffect, useState } from "react";
import { Wallet, TrendingUp, Receipt, PiggyBank, Sparkles } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Link } from "react-router-dom";
import StatCard from "../components/StatCard";
import { api } from "../lib/api";

export default function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [summary, setSummary] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [insights, setInsights] = useState([]);
  const [smartInsight, setSmartInsight] = useState(null);
  const [aiError, setAiError] = useState(null);

  useEffect(() => {
    api.getOverview().then(setOverview).catch(() => {});
    api.getSummary(6).then(setSummary).catch(() => {});
    api.getPrediction().then(setPrediction).catch(() => {});
    api.getPatternInsights().then(setInsights).catch(() => {});
    api.getSmartInsight().then((r) => setSmartInsight(r.insight)).catch((e) => setAiError(e.message));
  }, []);

  const chartData = summary.map((s) => ({ month: s.month, مجموع: s.total }));
  const fmt = (n) => Number(n || 0).toLocaleString("fa-IR");

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">داشبورد</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="مجموع هزینه‌ها" value={`${fmt(overview?.total_spent)} ت`} icon={Wallet} />
        <StatCard title="هزینه این ماه" value={`${fmt(overview?.this_month)} ت`} icon={Receipt} tone="danger" />
        <StatCard title="میانگین روزانه" value={`${fmt(overview?.avg_daily)} ت`} icon={TrendingUp} tone="accent" />
        <StatCard
          title="پیش‌بینی ماه آینده"
          value={`${fmt(prediction?.next_month_estimate)} ت`}
          sub={prediction ? `اعتماد: ${prediction.confidence}` : ""}
          icon={PiggyBank}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-surface border border-border rounded-2xl p-5">
          <h2 className="font-semibold mb-4">روند هزینه ۶ ماه اخیر</h2>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2f3e" />
              <XAxis dataKey="month" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip contentStyle={{ background: "#1f2330", border: "1px solid #2a2f3e", borderRadius: 8 }} />
              <Line type="monotone" dataKey="مجموع" stroke="#6366f1" strokeWidth={2.5} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-surface border border-border rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles size={18} className="text-primary" />
            <h2 className="font-semibold">تحلیل هوش مصنوعی</h2>
          </div>
          {aiError ? (
            <div className="text-sm text-gray-400 space-y-2">
              <p>سرویس AI فعال نیست.</p>
              <p className="text-xs text-gray-500">{aiError}</p>
              <Link to="/ai" className="text-primary text-xs">راهنمای فعال‌سازی ←</Link>
            </div>
          ) : smartInsight ? (
            <p className="text-sm text-gray-300 leading-7">{smartInsight}</p>
          ) : (
            <p className="text-sm text-gray-500">در حال تحلیل...</p>
          )}
        </div>
      </div>

      <div className="bg-surface border border-border rounded-2xl p-5">
        <h2 className="font-semibold mb-3">بینش‌های آماری</h2>
        <div className="grid sm:grid-cols-2 gap-3">
          {insights.map((ins, i) => (
            <div
              key={i}
              className={`rounded-xl p-3 text-sm border ${
                ins.severity === "warning"
                  ? "border-danger/30 bg-danger/5"
                  : ins.severity === "success"
                  ? "border-accent/30 bg-accent/5"
                  : "border-border bg-surface2"
              }`}
            >
              <p className="font-semibold mb-1">{ins.title}</p>
              <p className="text-gray-400 text-xs leading-6">{ins.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
