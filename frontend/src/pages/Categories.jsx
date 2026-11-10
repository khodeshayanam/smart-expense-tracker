import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { api } from "../lib/api";

const COLORS = ["#6366f1", "#ef4444", "#22c55e", "#f59e0b", "#06b6d4", "#ec4899", "#a855f7"];

export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", icon: "📦", color: COLORS[0] });
  const [error, setError] = useState(null);

  const load = () => api.getCategories().then(setCategories);

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      await api.createCategory(form);
      setForm({ name: "", icon: "📦", color: COLORS[0] });
      setShowForm(false);
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">دسته‌بندی‌ها</h1>
        <button
          onClick={() => setShowForm((s) => !s)}
          className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-xl text-sm font-semibold"
        >
          <Plus size={16} /> دسته جدید
        </button>
      </div>

      {showForm && (
        <form onSubmit={submit} className="bg-surface border border-border rounded-2xl p-4 flex flex-wrap gap-3 items-center">
          <input
            placeholder="ایموجی"
            value={form.icon}
            onChange={(e) => setForm((f) => ({ ...f, icon: e.target.value }))}
            className="w-16 bg-surface2 border border-border rounded-xl px-3 py-2 outline-none text-center"
          />
          <input
            placeholder="نام دسته"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            className="flex-1 min-w-[160px] bg-surface2 border border-border rounded-xl px-3 py-2 outline-none focus:border-primary"
          />
          <div className="flex gap-1">
            {COLORS.map((c) => (
              <button
                type="button"
                key={c}
                onClick={() => setForm((f) => ({ ...f, color: c }))}
                className={`w-7 h-7 rounded-full border-2 ${form.color === c ? "border-white" : "border-transparent"}`}
                style={{ background: c }}
              />
            ))}
          </div>
          <button className="bg-primary text-white px-4 py-2 rounded-xl text-sm font-semibold">افزودن</button>
          {error && <p className="text-danger text-xs w-full">{error}</p>}
        </form>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {categories.map((c) => (
          <div key={c.id} className="bg-surface border border-border rounded-xl p-4 flex items-center gap-3">
            <span className="text-2xl">{c.icon}</span>
            <div>
              <p className="font-medium text-sm">{c.name}</p>
              <span className="inline-block w-3 h-3 rounded-full mt-1" style={{ background: c.color }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
