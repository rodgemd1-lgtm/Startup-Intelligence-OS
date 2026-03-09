"use client";
import { useRouter } from "next/navigation";

const items = [
  { path: "/", icon: "\u25C6", label: "Home" },
  { path: "/decisions", icon: "\u2B21", label: "Decisions" },
  { path: "/capabilities", icon: "\u25CE", label: "Capabilities" },
  { path: "/innovation", icon: "\u2726", label: "Innovation" },
  { path: "/agents", icon: "\u2295", label: "Agents" },
  { path: "/dashboard", icon: "\u25C8", label: "25X" },
];

export function BottomNav({ currentPath }: { currentPath: string }) {
  const router = useRouter();
  return (
    <nav className="bottom-nav">
      {items.map((item) => (
        <div
          key={item.path}
          className={`bottom-nav-item${currentPath === item.path ? " active" : ""}`}
          onClick={() => router.push(item.path)}
        >
          <span className="bnav-icon">{item.icon}</span>
          {item.label}
        </div>
      ))}
    </nav>
  );
}
