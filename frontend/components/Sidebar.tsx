"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  LineChart,
  Newspaper,
  Briefcase,
  Filter,
  FileSearch,
  FileText,
  Bot,
  TrendingUp,
  Globe,
  Settings,
  LogOut,
  type LucideIcon,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { clsx } from "clsx";

const GROUPS: { title: string; items: { href: string; label: string; icon: LucideIcon }[] }[] = [
  {
    title: "Markets",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
      { href: "/stocks/AAPL", label: "Stocks", icon: LineChart },
      { href: "/news", label: "News", icon: Newspaper },
      { href: "/portfolio", label: "Portfolio", icon: Briefcase },
      { href: "/screener", label: "Screener", icon: Filter },
      { href: "/geo", label: "Geo Risk", icon: Globe },
    ],
  },
  {
    title: "AI Tools",
    items: [
      { href: "/research", label: "Research", icon: FileSearch },
      { href: "/reports", label: "Reports", icon: FileText },
      { href: "/memo", label: "AI Memo", icon: Bot },
      { href: "/economics", label: "Economics", icon: TrendingUp },
    ],
  },
];

function NavItem({
  href,
  label,
  icon: Icon,
  active,
}: {
  href: string;
  label: string;
  icon: LucideIcon;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className={clsx(
        "group flex items-center gap-3 rounded-lg px-2 py-1.5 text-sm transition-colors",
        active
          ? "font-medium text-terminal-text"
          : "text-terminal-muted hover:text-terminal-text"
      )}
    >
      <span
        className={clsx(
          "flex h-7 w-7 shrink-0 items-center justify-center rounded-md transition-colors",
          active
            ? "bg-terminal-amber/15 text-terminal-amber"
            : "bg-white/[0.04] text-terminal-muted group-hover:bg-white/[0.08] group-hover:text-terminal-text"
        )}
      >
        <Icon size={15} />
      </span>
      {label}
    </Link>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const isActive = (href: string) =>
    pathname.startsWith(href.split("/").slice(0, 2).join("/"));

  return (
    <aside className="flex h-screen w-60 flex-col border-r border-terminal-border bg-terminal-panel">
      <div className="flex items-center gap-2.5 px-5 py-5">
        <div className="h-2 w-2 rounded-full bg-terminal-amber" />
        <span className="text-sm font-semibold tracking-tight">AI Terminal</span>
      </div>

      <nav className="flex-1 space-y-6 overflow-y-auto px-3 pb-4">
        {GROUPS.map((group) => (
          <div key={group.title}>
            <div className="mb-2 px-2 text-[11px] font-semibold uppercase tracking-wider text-terminal-muted/70">
              {group.title}
            </div>
            <div className="space-y-1">
              {group.items.map((item) => (
                <NavItem key={item.href} {...item} active={isActive(item.href)} />
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-terminal-border px-3 py-3">
        <NavItem
          href="/settings"
          label="Settings"
          icon={Settings}
          active={isActive("/settings")}
        />
        <button
          onClick={logout}
          className="group flex w-full items-center gap-3 rounded-lg px-2 py-1.5 text-sm text-terminal-muted transition-colors hover:text-terminal-red"
        >
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-white/[0.04] text-terminal-muted transition-colors group-hover:bg-terminal-red/15 group-hover:text-terminal-red">
            <LogOut size={15} />
          </span>
          Logout
        </button>
        <div className="mt-2 truncate px-2 text-[11px] text-terminal-muted/70">
          {user?.email}
        </div>
      </div>
    </aside>
  );
}
