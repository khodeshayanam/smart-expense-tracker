export default function StatCard({ title, value, sub, icon: Icon, tone = "primary" }) {
  const toneMap = {
    primary: "text-primary bg-primary/10",
    accent: "text-accent bg-accent/10",
    danger: "text-danger bg-danger/10",
  };
  return (
    <div className="bg-surface border border-border rounded-2xl p-5 flex items-start justify-between">
      <div>
        <p className="text-sm text-gray-400 mb-1">{title}</p>
        <p className="text-2xl font-bold num">{value}</p>
        {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
      </div>
      {Icon && (
        <div className={`p-2.5 rounded-xl ${toneMap[tone]}`}>
          <Icon size={20} />
        </div>
      )}
    </div>
  );
}
