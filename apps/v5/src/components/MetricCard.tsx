"use client";

interface MetricCardProps {
  label: string;
  value: string | number;
  color: "accent" | "warning" | "success" | "danger";
  delay: number;
}

export function MetricCard({ label, value, color, delay }: MetricCardProps) {
  return (
    <div
      className={`metric-card m-${color} reveal`}
      style={{ "--d": `${delay}ms` } as React.CSSProperties}
    >
      <div className="metric-label">{label}</div>
      <div className={`metric-value ${color} count-up`}>{value}</div>
    </div>
  );
}
