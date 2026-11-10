import { NavLink } from "react-router-dom";
import { LayoutDashboard, Receipt, Target, Tags, Sparkles, Wallet } from "lucide-react";

const links = [
  { to: "/", label: "داشبورد", icon: LayoutDashboard },
  { to: "/expenses", label: "تراکنش‌ها", icon: Receipt },
  { to: "/habits", label: "عادت‌ها", icon: Target },
  { to: "/categories", label: "دسته‌بندی‌ها", icon: Tags },
  { to: "/ai", label: "دستیار هوشمند", icon: Sparkles },
];

export default function Sidebar() {
  return (
    <aside className="w-64 shrink-0 bg-surface border-l border-border h-screen sticky top-0 flex flex-col">
      <div className="flex items-center gap-2 px-6 py-5 border-b border-border">
        <Wallet className="text-primary" size={26} />
        <span className="font-bold text-lg">مدیریت هزینه</span>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors ${
                isActive
                  ? "bg-primary/15 text-primary font-semibold"
                  : "text-gray-400 hover:bg-surface2 hover:text-gray-200"
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-4 py-4 text-xs text-gray-500 border-t border-border">
        نسخه ۲.۰ — هوش مصنوعی فعال
      </div>
    </aside>
  );
}
