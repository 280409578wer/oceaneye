export type MetricKey = "cost" | "clicks" | "impressions" | "ctr" | "conversions" | "cpa" | "cvr";
export type IntervalKey = "5m" | "15m" | "30m" | "1h";

export interface Delta {
  absolute: number;
  percent: number | null;
  improving: boolean | null;
}

export interface Account {
  id: number;
  name: string;
  advertiser_id: string;
  balance: number;
  status: string;
  cost?: number;
  conversions?: number;
  cpa?: number | null;
  ctr?: number | null;
}

export interface Summary {
  cost: number;
  impressions: number;
  clicks: number;
  conversions: number;
  ctr: number | null;
  cvr: number | null;
  cpa: number | null;
  balance: number;
  budget: number;
  budget_usage: number | null;
  last_updated: string | null;
  comparison_window: string;
  deltas: Record<MetricKey, Delta>;
}

export interface TimePoint {
  timestamp: string;
  cost: number;
  impressions: number;
  clicks: number;
  conversions: number;
  ctr: number | null;
  cvr: number | null;
  cpa: number | null;
}

export interface Plan extends TimePoint {
  id: number;
  account_id: number;
  name: string;
  status: string;
  budget: number;
  profile: string;
  status_label: "强势" | "正常" | "观察" | "风险" | "异常";
  status_reason: string;
  risk_score: number;
  account_name?: string;
}

export interface AlertItem {
  id: number;
  account_id: number;
  plan_id: number | null;
  plan_name: string | null;
  account_name: string;
  type: string;
  severity: "positive" | "warning" | "danger";
  title: string;
  message: string;
  timestamp: string;
  read: number;
}

export interface Analysis {
  text: string;
  provider: string;
}

export interface AlertRule {
  id: number;
  rule_key: string;
  name: string;
  enabled: number;
  threshold: number;
  window_minutes: number;
}

export interface AppSettings {
  values: Record<string, string>;
  alert_rules: AlertRule[];
  data_source: string;
}

