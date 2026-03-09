"use client";
import { useRouter } from "next/navigation";
import type { AppContext } from "@/lib/state";

interface TopbarProps {
  context: AppContext;
}

export function Topbar({ context }: TopbarProps) {
  const router = useRouter();

  return (
    <div className="topbar">
      <div className="ctx-badges">
        <span className="badge">
          <span className="badge-label">company</span>
          {context.active_company}
        </span>
        <span className="badge">
          <span className="badge-label">project</span>
          {context.active_project}
        </span>
        <span className="badge">
          <span className="badge-label">decision</span>
          {context.active_decision}
        </span>
        <span className="badge">
          <span className="badge-label">branch</span>
          {context.active_branch}
        </span>
      </div>
      <div className="toolbar">
        <button className="btn" onClick={() => router.push("/agents")}>
          Run Susan
        </button>
        <button className="btn btn-primary" onClick={() => router.push("/decisions")}>
          Decision Room
        </button>
      </div>
    </div>
  );
}
