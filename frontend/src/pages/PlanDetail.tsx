import { ArrowLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { IntradayChart } from "../components/IntradayChart";
import { MetricCard } from "../components/MetricCard";
import type { IntervalKey, MetricKey, Plan, TimePoint } from "../types";

const money = (value: number | null | undefined) => value == null ? "--" : `¥${value.toFixed(2)}`;

export function PlanDetail() {
  const { id } = useParams();
  const planId = Number(id);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [series, setSeries] = useState<TimePoint[]>([]);
  const [interval, setIntervalKey] = useState<IntervalKey>("15m");
  const [metric, setMetric] = useState<MetricKey>("cost");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.plan(planId), api.planTimeseries(planId, interval)])
      .then(([nextPlan, nextSeries]) => { setPlan(nextPlan); setSeries(nextSeries); setError(""); })
      .catch((caught: Error) => setError(caught.message));
  }, [interval, planId]);

  if (error) return <div className="content-page"><div className="error-banner">{error}</div><Link to="/">返回行情</Link></div>;
  if (!plan) return <div className="page-state"><div className="loading-orbit" /><p>加载计划行情…</p></div>;
  return (
    <main className="content-page page-enter">
      <Link className="back-link" to="/"><ArrowLeft size={15} />返回行情</Link>
      <header className="detail-header"><div><span className="eyebrow">PLAN DETAIL · {plan.account_name}</span><h1>{plan.name}</h1><p>{plan.status_reason}</p></div><span className={`status-badge status-${plan.status_label}`}>{plan.status_label}</span></header>
      <section className="market-strip market-strip--detail">
        <MetricCard label="今日消耗" value={money(plan.cost)} emphasis /><MetricCard label="转化" value={String(plan.conversions)} />
        <MetricCard label="CPA" value={money(plan.cpa)} /><MetricCard label="点击" value={String(plan.clicks)} />
        <MetricCard label="展示" value={plan.impressions.toLocaleString("zh-CN")} /><MetricCard label="CTR" value={plan.ctr == null ? "--" : `${plan.ctr.toFixed(2)}%`} />
      </section>
      <section className="panel detail-chart-panel">
        <div className="panel-header panel-header--wrap"><div><span className="section-kicker">PLAN INTRADAY</span><h2>今日分时</h2></div>
          <div className="panel-controls"><div className="segmented">{(["cost", "conversions", "cpa", "ctr"] as MetricKey[]).map((key) => <button className={metric === key ? "active" : ""} onClick={() => setMetric(key)} key={key}>{({ cost: "消耗", conversions: "转化", cpa: "CPA", ctr: "CTR" } as Record<string, string>)[key]}</button>)}</div>
          <div className="segmented segmented--quiet">{(["5m", "15m", "30m", "1h"] as IntervalKey[]).map((key) => <button className={interval === key ? "active" : ""} onClick={() => setIntervalKey(key)} key={key}>{key}</button>)}</div></div>
        </div><IntradayChart data={series} metric={metric} />
      </section>
      <section className="detail-columns"><div className="panel mini-analysis"><span className="section-kicker">TIME COMPARISON</span><h2>时间对比</h2><p>V0.1 已在首页指标卡中提供“最近30分钟 vs 上一30分钟”。计划级多日期范围将在历史数据积累后启用。</p></div><div className="panel mini-analysis"><span className="section-kicker">AI ANALYSIS</span><h2>投放分析</h2><p>{plan.status_reason}。当前仅提供只读规则分析，不会对广告计划执行任何操作。</p></div></section>
    </main>
  );
}

