"use client";
import { useAppState } from "@/components/AppShell";
import { groupColors } from "@/lib/utils";

function delay(i: number) {
  return { style: { "--d": `${i * 60}ms` } as React.CSSProperties };
}

export default function AgentsPage() {
  const state = useAppState();

  // Group agents by group field
  const groups: Record<string, typeof state.agents> = {};
  state.agents.forEach((a) => {
    if (!groups[a.group]) groups[a.group] = [];
    groups[a.group].push(a);
  });

  const groupNames = Object.keys(groups);

  return (
    <>
      <h1
        className="reveal"
        {...delay(0)}
        style={{ marginBottom: 4, ...({ "--d": "0ms" } as React.CSSProperties) }}
      >
        Agent Console
      </h1>
      <p className="reveal" {...delay(0)}>
        {state.agents.length} agents across {groupNames.length} groups. The team
        behind the operating system.
      </p>

      {groupNames.map((group, idx) => {
        const gc = groupColors[group] || "#8ba4cc";
        return (
          <div className="reveal" key={group} {...delay(idx + 1)}>
            <div className="label" style={{ margin: "8px 0" }}>
              {group.toUpperCase()} ({groups[group].length})
            </div>
            <div className="grid-3">
              {groups[group].map((a) => (
                <div className="agent-card" key={a.name}>
                  <div className="agent-name">{a.name}</div>
                  <div className="agent-role">{a.role}</div>
                  <div
                    className="agent-group-badge"
                    style={{
                      background: `${gc}20`,
                      color: gc,
                    }}
                  >
                    {group}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </>
  );
}
