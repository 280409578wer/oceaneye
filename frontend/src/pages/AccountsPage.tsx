import { useEffect, useState } from "react";
import { api } from "../api";
import type { Account } from "../types";

export function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [error, setError] = useState("");
  useEffect(() => { api.accounts().then(setAccounts).catch((caught: Error) => setError(caught.message)); }, []);
  return <main className="content-page page-enter"><header className="content-header"><span className="eyebrow">ACCOUNT RANKING</span><h1>账户排行</h1><p>多个广告账户的今日表现对比</p></header>{error && <div className="error-banner">{error}</div>}<section className="panel"><div className="table-wrap"><table className="market-table"><thead><tr><th>账户</th><th>今日消耗</th><th>转化</th><th>CPA</th><th>CTR</th><th>状态</th></tr></thead><tbody>{accounts.sort((a,b)=>(b.conversions ?? 0)-(a.conversions ?? 0)).map((account, index) => <tr key={account.id}><td><strong>#{index + 1}　{account.name}</strong><span className="row-subtitle">{account.advertiser_id}</span></td><td className="mono">¥{(account.cost ?? 0).toFixed(2)}</td><td className="mono positive-text">{account.conversions ?? 0}</td><td className="mono">{account.cpa == null ? "--" : `¥${account.cpa.toFixed(2)}`}</td><td className="mono">{account.ctr == null ? "--" : `${account.ctr.toFixed(2)}%`}</td><td><span className="status-badge status-正常">正常</span></td></tr>)}</tbody></table></div></section></main>;
}

