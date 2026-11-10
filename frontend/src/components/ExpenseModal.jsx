import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { api } from "../lib/api";

export default function ExpenseModal({ categories, onClose, onSaved }) {
  const [form, setForm] = useState({
    amount: "",
    description: "",
    date: new Date().toISOString().slice(0, 10),
    category_id: categories[0]?.id || "",
    tx_type: "expense",
    notes: "",
  });
  const [suggestion, setSuggestion] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const t = setTimeout(async () => {
      if (form.description.length >= 2) {
        try {
          const r = await api.suggestCategory(form.description);
          setSuggestion(r.suggested_category);
        } catch {
          setSuggestion(null);
        }
      }
    }, 400);
    return () => clearTimeout(t);
  }, [form.description]);

  const applySuggestion = () => {
    const cat = categories.find((c) => c.name === suggestion);
    if (cat) setForm((f) => ({ ...f, category_id: cat.id }));
  };

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await api.createExpense({
        ...form,
        amount: Number(form.amount),
        category_id: Number(form.category_id),
      });
      onSaved();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-surface border border-border rounded-2xl w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-lg">ثبت تراکنش جدید</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={submit} className="space-y-3">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setForm((f) => ({ ...f, tx_type: "expense" }))}
              className={`flex-1 py-2 rounded-xl text-sm ${
                form.tx_type === "expense" ? "bg-danger/20 text-danger" : "bg-surface2 text-gray-400"
              }`}
            >
              هزینه
            </button>
            <button
              type="button"
              onClick={() => setForm((f) => ({ ...f, tx_type: "income" }))}
              className={`flex-1 py-2 rounded-xl text-sm ${
                form.tx_type === "income" ? "bg-accent/20 text-accent" : "bg-surface2 text-gray-400"
              }`}
            >
              درآمد
            </button>
          </div>

          <input
            required
            type="number"
            placeholder="مبلغ (تومان)"
            value={form.amount}
            onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
            className="w-full bg-surface2 border border-border rounded-xl px-3 py-2 outline-none focus:border-primary num"
          />

          <input
            required
            placeholder="توضیح (مثلاً: ناهار کبابی)"
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            className="w-full bg-surface2 border border-border rounded-xl px-3 py-2 outline-none focus:border-primary"
          />

          {suggestion && (
            <button
              type="button"
              onClick={applySuggestion}
              className="text-xs text-primary bg-primary/10 px-3 py-1.5 rounded-lg"
            >
              پیشنهاد هوشمند دسته: «{suggestion}» — اعمال کن
            </button>
          )}

          <select
            value={form.category_id}
            onChange={(e) => setForm((f) => ({ ...f, category_id: e.target.value }))}
            className="w-full bg-surface2 border border-border rounded-xl px-3 py-2 outline-none focus:border-primary"
          >
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.icon} {c.name}
              </option>
            ))}
          </select>

          <input
            required
            type="date"
            value={form.date}
            onChange={(e) => setForm((f) => ({ ...f, date: e.target.value }))}
            className="w-full bg-surface2 border border-border rounded-xl px-3 py-2 outline-none focus:border-primary num"
          />

          {error && <p className="text-danger text-sm">{error}</p>}

          <button
            disabled={saving}
            className="w-full bg-primary hover:bg-primary/90 transition-colors text-white rounded-xl py-2.5 font-semibold disabled:opacity-50"
          >
            {saving ? "در حال ثبت..." : "ثبت تراکنش"}
          </button>
        </form>
      </div>
    </div>
  );
}
