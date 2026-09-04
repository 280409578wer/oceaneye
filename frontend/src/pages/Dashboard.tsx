import { Bell, Expand, Pause, Play, RefreshCw, Search, Wifi } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api";
import { AlertsPanel } from "../components/AlertsPanel";
import { IntradayChart } from "../components/IntradayChart";
import { MetricCard } from "../components/MetricCard";
import { PlanTable } from "../components/PlanTable";
import type { Account, AlertItem, Analysis, IntervalKey, MetricKey, Plan, Summary, TimePoint } from "../types";

const metricTabs: Array<{ key: MetricKey; label: string }> = [
  { key: "cost", label: "消耗" }, { key: "conversions", label: "转化" }, { key: "cpa", label: "CPA" },
  { key: "clicks", label: "点击" }, { key: "ctr", label: "CTR" }, { key: "impressions", label: "展示" }, { key: "cvr", label: "CVR" },
];
const intervalTabs: Array<{ key: IntervalKey; label: string }> = [
  { key: "5m", label: "5分钟" }, { key: "15m", label: "15分钟" }, { key: "30m", label: "30分钟" }, { key: "1h", label: "1小时" },
];
const money = (value: number | null | undefined) => value == null ? "--" : `¥${value.toLocaleString("zh-CN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const number = (value: number | null | undefined) => value == null ? "--" : value.toLocaleString("zh-CN");
const percent = (value: number | null | undefined) => value == null ? "--" : `${value.toFixed(2)}%`;

export function Dashboard() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [accountId, setAccountId] = useState(() => Number(localStorage.getItem("oceaneye:lastAccountId")) || 1);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [series, setSeries] = useState<TimePoint[]>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [metric, setMetric] = useState<MetricKey>("cost");
  const [interval, setIntervalKey] = useState<IntervalKey>("15m");
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshSeconds, setRefreshSeconds] = useState(10);
  const [countdown, setCountdown] = useState(10);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const firstAlertRef = useRef<number | null>(null);

  const loadAccountData = useCallback(async (showSpinner = false) => {
    if (showSpinner) setRefreshing(true);
    try {
      const [nextSummary, nextSeries, nextPlans, nextAlerts, nextAnalysis] = await Promise.all([
        api.summary(accountId), api.timeseries(accountId, interval), api.plans(accountId), api.alerts(accountId), api.analysis(accountId),
      ]);
      setSummary(nextSummary); setSeries(nextSeries); setPlans(nextPlans); setAlerts(nextAlerts); setAnalysis(nextAnalysis);
      setError("");
      if (nextAlerts[0]) {
        if (firstAlertRef.current != null && nextAlerts[0].id !== firstAlertRef.current) setToast(`${nextAlerts[0].plan_name ?? "账户"}：${nextAlerts[0].title}`);
        firstAlertRef.current = nextAlerts[0].id;
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "数据加载失败");
    } finally {
      setLoading(false); setRefreshing(false); setCountdown(refreshSeconds);
    }
  }, [accountId, interval, refreshSeconds]);

  useEffect(() => {
    api.accounts().then((items) => {
      setAccounts(items);
      if (items.length && !items.some((item) => item.id === accountId)) setAccountId(items[0].id);
    }).catch((caught: Error) => setError(caught.message));
  }, [accountId]);

  useEffect(() => { localStorage.setItem("oceaneye:lastAccountId", String(accountId)); loadAccountData(); }, [accountId, interval, loadAccountData]);
  useEffect(() => {
    if (!autoRefresh) return;
    const refreshTimer = window.setInterval(() => loadAccountData(), refreshSeconds * 1000);
    const countdownTimer = window.setInterval(() => setCountdown((value) => value <= 1 ? refreshSeconds : value - 1), 1000);
    return () => { window.clearInterval(refreshTimer); window.clearInterval(countdownTimer); };
  }, [autoRefresh, loadAccountData, refreshSeconds]);
  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(""), 4000);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const enableNotifications = async () => {
    if (!("Notification" in window)) return setToast("当前浏览器不支持桌面通知");
    const permission = await Notification.requestPermission();
    setToast(permission === "granted" ? "浏览器通知已开启" : "未开启浏览器通知");
  };
  const fullscreen = () => document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();

  if (loading) return <div className="page-state"><div className="loading-orbit" /><p>正在接入 Mock 行情…</p></div>;

  return (
    <main className="dashboard page-enter">
      <header className="topbar">
        <div>
          <div className="eyebrow">OCEANEYE TERMINAL · MOCK DATA</div>
          <div className="topbar__title"><h1>巨量行情</h1><span className="connection"><i /><Wifi size={13} />连接正常</span></div>
        </div>
        <div className="topbar__tools">
          <label className="search-box"><Search size={16} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="搜索账户 / 计划" /></label>
          <select className="account-select" value={accountId} onChange={(event) => setAccountId(Number(event.target.value))} aria-label="切换账户">
            {accounts.map((account) => <option value={account.id} key={account.id}>{account.name}</option>)}
          </select>
          <button className="icon-button" onClick={enableNotifications} title="开启浏览器通知"><Bell size={17} /><span className="notification-dot" /></button>
          <button className="icon-button" onClick={fullscreen} title="全屏看盘"><Expand size={17} /></button>
        </div>
      </header>

      {error && <div className="error-banner"><strong>连接中断</strong><span>{error}。系统会继续尝试连接，页面不会崩溃。</span><button onClick={() => loadAccountData(true)}>重试</button></div>}

      <section className="market-strip">
        <MetricCard label="今日消耗" value={money(summary?.cost)} delta={summary?.deltas.cost} emphasis />
        <MetricCard label="今日转化" value={number(summary?.conversions)} delta={summary?.deltas.conversions} />
        <MetricCard label="平均 CPA" value={money(summary?.cpa)} delta={summary?.deltas.cpa} hint="下降为改善" />
        <MetricCard label="点击" value={number(summary?.clicks)} delta={summary?.deltas.clicks} />
        <MetricCard label="展示" value={number(summary?.impressions)} delta={summary?.deltas.impressions} />
        <MetricCard label="CTR" value={percent(summary?.ctr)} delta={summary?.deltas.ctr} />
        <MetricCard label="CVR" value={percent(summary?.cvr)} delta={summary?.deltas.cvr} />
        <MetricCard label="账户余额" value={money(summary?.balance)} hint={`预算使用 ${summary?.budget_usage ?? 0}%`} />
      </section>

      <section className="dashboard-grid dashboard-grid--top">
        <div className="panel chart-panel">
          <div className="panel-header panel-header--wrap">
            <div><span className="section-kicker">INTRADAY</span><h2>今日实时分时</h2></div>
            <div className="panel-controls">
              <div className="segmented">{metricTabs.map((item) => <button key={item.key} onClick={() => setMetric(item.key)} className={metric === item.key ? "active" : ""}>{item.label}</button>)}</div>
              <div className="segmented segmented--quiet">{intervalTabs.map((item) => <button key={item.key} onClick={() => setIntervalKey(item.key)} className={interval === item.key ? "active" : ""}>{item.label}</button>)}</div>
            </div>
          </div>
          <IntradayChart data={series} metric={metric} />
          <div className="chart-footer"><span>滚轮缩放 · 拖动查看</span><span>统计数据可能受平台延迟影响</span></div>
        </div>
        <div className="panel alerts-panel">
          <div className="panel-header"><div><span className="section-kicker">LIVE SIGNALS</span><h2>实时异动</h2></div><span className="live-pill"><i /> LIVE</span></div>
          <AlertsPanel alerts={alerts} />
        </div>
      </section>

      <section className="dashboard-grid dashboard-grid--bottom">
        <div className="panel plans-panel">
          <div className="panel-header"><div><span className="section-kicker">WATCHLIST</span><h2>广告计划行情</h2></div><span className="panel-note">点击表头排序 · 点击计划看详情</span></div>
          <PlanTable plans={plans} search={search} />
        </div>
        <div className="panel ai-panel">
          <div className="panel-header"><div><span className="section-kicker">RULE INSIGHT</span><h2>AI 看盘</h2></div><span className="ai-badge">只读分析</span></div>
          <div className="ai-copy">{analysis?.text.split("\n").map((line, index) => line ? <p key={index}>{line}</p> : null)}</div>
          <div className="ai-disclaimer">基于规则与模板生成，不会暂停计划、修改预算或出价。</div>
        </div>
      </section>

      <footer className="terminal-footer">
        <div><span className="status-dot" />数据源 MOCK</div>
        <div>最后数据更新 <strong className="mono">{summary?.last_updated ? new Date(summary.last_updated).toLocaleTimeString("zh-CN") : "--"}</strong></div>
        <div className="refresh-controls">
          <button onClick={() => setAutoRefresh((value) => !value)}>{autoRefresh ? <Pause size={13} /> : <Play size={13} />}{autoRefresh ? "暂停刷新" : "开启刷新"}</button>
          <select value={refreshSeconds} onChange={(event) => { setRefreshSeconds(Number(event.target.value)); setCountdown(Number(event.target.value)); }}>
            <option value={10}>10秒</option><option value={60}>1分钟</option><option value={300}>5分钟</option><option value={900}>15分钟</option>
          </select>
          <button onClick={() => loadAccountData(true)}><RefreshCw size={13} className={refreshing ? "spin" : ""} />立即刷新</button>
          <span>下一次刷新 {autoRefresh ? `${countdown} 秒` : "已暂停"}</span>
        </div>
      </footer>
      {toast && <div className="toast"><span className="toast__icon">!</span>{toast}</div>}
    </main>
  );
}

