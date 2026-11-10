import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import ExpenseModal from "../components/ExpenseModal";
import { api } from "../lib/api";

export default function Expenses() {
  const [expenses, setExpenses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const [exps, cats] = await Promise.all([api.getExpenses({ limit: 100 }), api.getCategories()]);
    setExpenses(exps);
    setCategories(cats);
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, []);

  const remove = async (id) => {
    if (!confirm("این تراکنش حذف شود؟")) return;
    await api.deleteExpense(id);
    load();
  };

  const fmt = (n) => Number(n).toLocaleString("fa-IR");

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">تراکنش‌ها</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-xl text-sm font-semibold"
        >
          <Plus size={16} /> تراکنش جدید
        </button>
      </div>

      <div className="bg-surface border border-border rounded-2xl overflow-hidden">
        {loading ? (
          <p className="p-6 text-gray-500 text-sm">در حال بارگذاری...</p>
        ) : expenses.length === 0 ? (
          <p className="p-6 text-gray-500 text-sm">هنوز تراکنشی ثبت نشده.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-surface2 text-gray-400">
              <tr>
                <th className="text-right px-4 py-3 font-medium">توضیح</th>
                <th className="text-right px-4 py-3 font-medium">دسته</th>
                <th className="text-right px-4 py-3 font-medium">تاریخ</th>
                <th className="text-right px-4 py-3 font-medium">مبلغ</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {expenses.map((e) => (
                <tr key={e.id} className="border-t border-border hover:bg-surface2/50">
                  <td className="px-4 py-3">{e.description}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1.5">
                      {e.category?.icon} {e.category?.name}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-400 num">{e.date}</td>
                  <td className={`px-4 py-3 num font-semibold ${e.tx_type === "income" ? "text-accent" : "text-gray-200"}`}>
                    {e.tx_type === "income" ? "+" : "-"}
                    {fmt(e.amount)} ت
                  </td>
                  <td className="px-4 py-3 text-left">
                    <button onClick={() => remove(e.id)} className="text-gray-500 hover:text-danger">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <ExpenseModal
          categories={categories}
          onClose={() => setShowModal(false)}
          onSaved={() => {
            setShowModal(false);
            load();
          }}
        />
      )}
    </div>
  );
}
