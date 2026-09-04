import { useEffect, useState } from "react";
import { api } from "../api";
import { AlertsPanel } from "../components/AlertsPanel";
import type { AlertItem } from "../types";

export function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  useEffect(() => { api.alerts().then(setAlerts).catch(() => setAlerts([])); }, []);
  return <main className="content-page page-enter"><header className="content-header"><span className="eyebrow">ALL SIGNALS</span><h1>实时异动</h1><p>跨账户查看转化、消耗、CPA 与余额预警</p></header><section className="panel standalone-alerts"><AlertsPanel alerts={alerts} /></section></main>;
}

