import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Plan } from "../types";

type SortKey = "cost" | "conversions" | "cpa" | "ctr" | "risk_score";

const money = (value: number | null | undefined) => value == null ? "--" : `¥${value.toFixed(2)}`;
const percent = (value: number | null | undefined) => value == null ? "--" : `${value.toFixed(2)}%`;

export function PlanTable({ plans, search = "" }: { plans: Plan[]; search?: string }) {
  const navigate = useNavigate();
  const [sort, setSort] = useState<SortKey>("cost");
  const [ascending, setAscending] = useState(false);
  const rows = useMemo(() => {
    const term = search.trim().toLowerCase();
    return plans
      .filter((plan) => !term || plan.name.toLowerCase().includes(term))
      .sort((a, b) => {
        const left = a[sort] ?? Number.POSITIVE_INFINITY;
        const right = b[sort] ?? Number.POSITIVE_INFINITY;
        return (Number(left) - Number(right)) * (ascending ? 1 : -1);
      });
  }, [ascending, plans, search, sort]);

  const toggleSort = (key: SortKey) => {
    if (sort === key) setAscending((value) => !value);
    else {
      setSort(key);
      setAscending(key === "cpa");
    }
  };

  const header = (key: SortKey, label: string) => (
    <button className={sort === key ? "sort-button sort-button--active" : "sort-button"} onClick={() => toggleSort(key)}>
      {label} {sort === key ? (ascending ? "↑" : "↓") : ""}
    </button>
  );

  return (
    <div className="table-wrap">
      <table className="market-table">
        <thead><tr>
          <th>计划</th><th>{header("cost", "消耗")}</th><th>{header("conversions", "转化")}</th>
          <th>{header("cpa", "CPA")}</th><th>{header("ctr", "CTR")}</th><th>CVR</th><th>{header("risk_score", "状态")}</th>
        </tr></thead>
        <tbody>
          {rows.map((plan) => (
            <tr key={plan.id} onClick={() => navigate(`/plan/${plan.id}`)} tabIndex={0}>
              <td><strong>{plan.name}</strong><span className="row-subtitle">预算 {money(plan.budget)}</span></td>
              <td className="mono">{money(plan.cost)}</td>
              <td className="mono positive-text">{plan.conversions}</td>
              <td className={`mono ${plan.status_label === "风险" || plan.status_label === "异常" ? "negative-text" : ""}`}>{money(plan.cpa)}</td>
              <td className="mono">{percent(plan.ctr)}</td>
              <td className="mono">{percent(plan.cvr)}</td>
              <td><span className={`status-badge status-${plan.status_label}`}>{plan.status_label}</span><span className="row-subtitle">{plan.status_reason}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
      {!rows.length && <div className="empty-state">没有找到匹配的计划</div>}
    </div>
  );
}

