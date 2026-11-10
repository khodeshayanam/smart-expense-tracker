import { useState } from "react";
import { Sparkles, Send, AlertTriangle } from "lucide-react";
import { api } from "../lib/api";

export default function AIInsights() {
  const [messages, setMessages] = useState([
    { role: "ai", text: "سلام! درباره وضعیت مالی‌ات هر سوالی داری بپرس — مثلاً «این ماه بیشتر کجا خرج کردم؟»" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [notConfigured, setNotConfigured] = useState(false);

  const send = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const q = input.trim();
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setLoading(true);
    try {
      const r = await api.askAI(q);
      setMessages((m) => [...m, { role: "ai", text: r.answer }]);
    } catch (err) {
      if (err.message.includes("GEMINI_API_KEY")) setNotConfigured(true);
      setMessages((m) => [...m, { role: "ai", text: `خطا: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5 max-w-3xl">
      <div className="flex items-center gap-2">
        <Sparkles className="text-primary" size={22} />
        <h1 className="text-2xl font-bold">دستیار هوشمند</h1>
      </div>

      {notConfigured && (
        <div className="bg-danger/10 border border-danger/30 rounded-2xl p-4 text-sm space-y-2">
          <div className="flex items-center gap-2 font-semibold text-danger">
            <AlertTriangle size={16} /> کلید هوش مصنوعی تنظیم نشده
          </div>
          <p className="text-gray-300">برای فعال‌سازی دستیار هوشمند:</p>
          <ol className="list-decimal pr-5 text-gray-400 space-y-1">
            <li>به <code className="bg-surface2 px-1 rounded">aistudio.google.com/apikey</code> برو و یک کلید رایگان بساز</li>
            <li>یک فایل به نام <code className="bg-surface2 px-1 rounded">backend/.env</code> بساز</li>
            <li>این خط را داخلش بگذار: <code className="bg-surface2 px-1 rounded">GEMINI_API_KEY=کلید_تو</code></li>
            <li>بک‌اند را دوباره اجرا کن</li>
          </ol>
        </div>
      )}

      <div className="bg-surface border border-border rounded-2xl flex flex-col h-[480px]">
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-start" : "justify-end"}`}>
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-7 ${
                  m.role === "user" ? "bg-primary text-white" : "bg-surface2 text-gray-200"
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}
          {loading && <p className="text-xs text-gray-500">در حال فکر کردن...</p>}
        </div>
        <form onSubmit={send} className="border-t border-border p-3 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="سوالت رو بنویس..."
            className="flex-1 bg-surface2 border border-border rounded-xl px-3 py-2 outline-none focus:border-primary"
          />
          <button className="bg-primary text-white p-2.5 rounded-xl">
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
