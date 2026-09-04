import type { AlertItem } from "../types";

export function AlertsPanel({ alerts }: { alerts: AlertItem[] }) {
  return (
    <div className="alerts-list">
      {alerts.slice(0, 8).map((alert) => {
        const time = new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(new Date(alert.timestamp));
        return (
          <div className={`alert-row alert-row--${alert.severity}`} key={alert.id}>
            <div className="alert-row__rail" />
            <div className="alert-row__time mono">{time}</div>
            <div className="alert-row__body">
              <div><strong>{alert.plan_name ?? alert.account_name}</strong><span className="alert-row__title">{alert.title}</span></div>
              <p>{alert.message}</p>
            </div>
          </div>
        );
      })}
      {!alerts.length && <div className="empty-state">当前没有异动</div>}
    </div>
  );
}

