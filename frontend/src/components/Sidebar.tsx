import { Activity, BellRing, FileBarChart, Import, LayoutDashboard, Palette, Settings, Users } from "lucide-react";
import { NavLink } from "react-router-dom";

const items = [
  { to: "/", label: "行情", icon: LayoutDashboard },
  { to: "/accounts", label: "账户", icon: Users },
  { to: "/alerts", label: "异动", icon: Activity },
  { to: "/reports", label: "日报", icon: FileBarChart },
  { to: "/import", label: "导入", icon: Import },
  { to: "/materials", label: "素材检测", icon: Palette },
  { to: "/settings/alerts", label: "预警设置", icon: BellRing },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand-mark">OE</div>
      <nav>
        {items.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => isActive ? "nav-item nav-item--active" : "nav-item"} title={label}>
            <Icon size={19} /><span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar__bottom"><Settings size={17} /><span>V0.1</span></div>
    </aside>
  );
}

