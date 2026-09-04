import type { Account, AlertItem, Analysis, AppSettings, IntervalKey, Plan, Summary, TimePoint } from "./types";

const API_ROOT = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_ROOT}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!response.ok) {
    let message = `请求失败（${response.status}）`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) message = body.detail;
    } catch {
      // 保留统一错误文案
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export const api = {
  accounts: () => request<Account[]>("/accounts"),
  account: (id: number) => request<Account>(`/accounts/${id}`),
  summary: (id: number) => request<Summary>(`/accounts/${id}/summary`),
  timeseries: (id: number, interval: IntervalKey) => request<TimePoint[]>(`/accounts/${id}/timeseries?interval=${interval}`),
  plans: (id: number) => request<Plan[]>(`/accounts/${id}/plans`),
  analysis: (id: number) => request<Analysis>(`/accounts/${id}/analysis`),
  alerts: (id?: number) => request<AlertItem[]>(`/alerts${id ? `?account_id=${id}` : ""}`),
  plan: (id: number) => request<Plan>(`/plans/${id}`),
  planTimeseries: (id: number, interval: IntervalKey) => request<TimePoint[]>(`/plans/${id}/timeseries?interval=${interval}`),
  settings: () => request<AppSettings>("/settings"),
  updateSettings: (payload: object) => request<AppSettings>("/settings", { method: "PUT", body: JSON.stringify(payload) }),
};
