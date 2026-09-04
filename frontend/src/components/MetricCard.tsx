import type { Delta } from "../types";

interface MetricCardProps {
  label: string;
  value: string;
  delta?: Delta;
  hint?: string;
  emphasis?: boolean;
}

export function MetricCard({ label, value, delta, hint, emphasis }: MetricCardProps) {
  const direction = !delta || delta.absolute === 0 ? "→" : delta.absolute > 0 ? "↑" : "↓";
  const tone = delta?.improving === true ? "positive" : delta?.improving === false ? "negative" : "neutral";
  const change = delta?.percent == null ? "暂无对比" : `${Math.abs(delta.percent).toFixed(1)}%`;

  return (
    <div className={`metric-card ${emphasis ? "metric-card--emphasis" : ""}`}>
      <div className="metric-card__label">{label}</div>
      <div className="metric-card__value mono">{value}</div>
      <div className={`metric-card__delta metric-card__delta--${tone}`}>
        <span>{direction}</span>
        <span>{change}</span>
        {hint && <span className="metric-card__hint">{hint}</span>}
      </div>
    </div>
  );
}

