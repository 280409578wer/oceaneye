import { Save } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api";
import type { AlertRule } from "../types";

export function AlertSettingsPage() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  useEffect(() => { api.settings().then((data) => setRules(data.alert_rules)).catch((caught: Error) => setError(caught.message)); }, []);
  const save = async () => {
    try { const data = await api.updateSettings({ alert_rules: rules }); setRules(data.alert_rules); setMessage("预警规则已保存"); setError(""); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "保存失败"); }
  };
  return <main className="content-page page-enter"><header className="content-header"><span className="eyebrow">ALERT RULES</span><h1>预警设置</h1><p>所有阈值保存在 SQLite，可随时调整，不会修改广告账户。</p></header>{error && <div className="error-banner">{error}</div>}<section className="panel settings-list">{rules.map((rule, index) => <div className="settings-row" key={rule.id}><label className="switch"><input type="checkbox" checked={Boolean(rule.enabled)} onChange={(event) => setRules((items) => items.map((item, i) => i === index ? { ...item, enabled: Number(event.target.checked) } : item))} /><span /></label><div><strong>{rule.name}</strong><p>{rule.rule_key}</p></div><label>时间窗口<input type="number" min={5} value={rule.window_minutes} onChange={(event) => setRules((items) => items.map((item, i) => i === index ? { ...item, window_minutes: Number(event.target.value) } : item))} />分钟</label><label>触发阈值<input type="number" min={0} step="0.1" value={rule.threshold} onChange={(event) => setRules((items) => items.map((item, i) => i === index ? { ...item, threshold: Number(event.target.value) } : item))} /></label></div>)}<div className="settings-actions"><button className="primary-button" onClick={save}><Save size={15} />保存设置</button>{message && <span className="positive-text">{message}</span>}</div></section></main>;
}

