"use client";
import { useRouter } from "next/navigation";

interface SidebarProps {
  currentPath: string;
  apiLive: boolean;
  agentCount: number;
  decisionCount: number;
  totalGaps: number;
}

const workspaces = [
  { name: "Founder Intelligence OS", meta: "main \u00B7 decision-capability-os", active: true, live: true },
  { name: "TransformFit", meta: "main \u00B7 motion-ui", active: false, live: false },
  { name: "Oracle Health AI", meta: "main \u00B7 enablement", active: false, live: false },
];

const teamItems = [
  { id: "jake", label: "Jake", active: true },
  { id: "susan", label: "Susan", active: false },
  { id: "research", label: "Research", active: false },
  { id: "build", label: "Build", active: false },
];

export function Sidebar({ currentPath, apiLive, agentCount, decisionCount, totalGaps }: SidebarProps) {
  const router = useRouter();

  const navItems = [
    { path: "/", icon: "\u25C6", label: "Workspace Home", badge: null as (() => number) | null, badgeType: "" },
    { path: "/decisions", icon: "\u2B21", label: "Decision Room", badge: () => decisionCount, badgeType: "accent-badge" },
    { path: "/capabilities", icon: "\u25CE", label: "Capability Map", badge: () => totalGaps, badgeType: "danger-badge" },
    { path: "/innovation", icon: "\u2726", label: "Innovation Studio", badge: null as (() => number) | null, badgeType: "" },
    { path: "/agents", icon: "\u2295", label: "Agent Console", badge: () => agentCount, badgeType: "accent-badge" },
    { path: "/dashboard", icon: "\u25C8", label: "25X Dashboard", badge: null as (() => number) | null, badgeType: "" },
  ];

  return (
    <aside className="sidebar">
      <div className="logo">
        <div className="logo-mark">J</div>
        <div>
          <div className="logo-text">Jake Console</div>
          <div className="logo-sub">Startup Intelligence OS v5</div>
        </div>
      </div>

      <div className="section-label">Workspaces</div>
      <div>
        {workspaces.map((ws) => (
          <div
            key={ws.name}
            className={`workspace-card${ws.active ? " active" : ""}`}
          >
            <div className="ws-name">
              <span className={`ws-dot ${ws.live ? "live" : "idle"}`} />
              {ws.name}
            </div>
            <div className="ws-meta">{ws.meta}</div>
          </div>
        ))}
      </div>

      <div className="section-label">Navigation</div>
      <div>
        {navItems.map((item) => (
          <div
            key={item.path}
            className={`nav-item${currentPath === item.path ? " active" : ""}`}
            onClick={() => router.push(item.path)}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
            {item.badge && (
              <span className={`nav-badge ${item.badgeType}`}>
                {item.badge()}
              </span>
            )}
          </div>
        ))}
      </div>

      <div className="section-label">Team</div>
      <div>
        {teamItems.map((t) => (
          <div
            key={t.id}
            className={`nav-item${t.active ? " active" : ""}`}
          >
            <span className="nav-icon">{"\u25CF"}</span>
            {t.label}
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        {apiLive ? `API: live \u00B7 ${agentCount} agents` : `Static mode \u00B7 ${agentCount} agents`}
      </div>
    </aside>
  );
}
