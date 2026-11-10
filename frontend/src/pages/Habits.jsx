import { useEffect, useState } from "react";
import { Plus, Flame, Check } from "lucide-react";
import { api } from "../lib/api";

export default function Habits() {
  const [habits, setHabits] = useState([]);
  const [streaks, setStreaks] = useState({});
  const [newName, setNewName] = useState("");
  const [showForm, setShowForm] = useState(false);

  const load = async () => {
    const list = await api.getHabits();
    setHabits(list);
    const entries = await Promise.all(
      list.map(async (h) => [h.id, await api.getHabitStreak(h.id)])
    );
    setStreaks(Object.fromEntries(entries));
  };

  useEffect(() => {
    load();
  }, []);

  const addHabit = async (e) => {
    e.preventDefault();
    if (!newName.trim()) return;
    await api.createHabit({ name: newName, target_frequency: "daily" });
    setNewName("");
    setShowForm(false);
    load();
  };

  const markToday = async (habitId) => {
    await api.logHabit({ habit_id: habitId, date: new Date().toISOString().slice(0, 10), completed: true });
    load();
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">عادت‌ها</h1>
        <button
          onClick={() => setShowForm((s) => !s)}
          className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-xl text-sm font-semibold"
        >
          <Plus size={16} /> عادت جدید
        </button>
      </div>

      {showForm && (
        <form onSubmit={addHabit} className="flex gap-2 bg-surface border border-border rounded-2xl p-4">
          <input
            autoFocus
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="مثلاً: ثبت روزانه هزینه‌ها"
            className="flex-1 bg-surface2 border border-border rounded-xl px-3 py-2 outline-none focus:border-primary"
          />
          <button className="bg-primary text-white px-4 rounded-xl text-sm font-semibold">افزودن</button>
        </form>
      )}

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {habits.map((h) => {
          const s = streaks[h.id];
          return (
            <div key={h.id} className="bg-surface border border-border rounded-2xl p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xl">{h.icon}</span>
                <button
                  onClick={() => markToday(h.id)}
                  className="bg-accent/15 text-accent p-1.5 rounded-lg hover:bg-accent/25"
                  title="ثبت امروز"
                >
                  <Check size={16} />
                </button>
              </div>
              <p className="font-semibold mb-2">{h.name}</p>
              <div className="flex items-center gap-1 text-sm text-orange-400">
                <Flame size={15} />
                <span className="num">{s?.current_streak ?? 0}</span>
                <span className="text-gray-500 text-xs">روز متوالی</span>
              </div>
            </div>
          );
        })}
        {habits.length === 0 && <p className="text-gray-500 text-sm">هنوز عادتی ثبت نشده.</p>}
      </div>
    </div>
  );
}
