import { Route, Routes } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { AccountsPage } from "./pages/AccountsPage";
import { AlertsPage } from "./pages/AlertsPage";
import { AlertSettingsPage } from "./pages/AlertSettingsPage";
import { Dashboard } from "./pages/Dashboard";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import { PlanDetail } from "./pages/PlanDetail";

export default function App() {
  return <div className="app-shell"><Sidebar /><div className="app-content"><Routes>
    <Route path="/" element={<Dashboard />} />
    <Route path="/plan/:id" element={<PlanDetail />} />
    <Route path="/accounts" element={<AccountsPage />} />
    <Route path="/alerts" element={<AlertsPage />} />
    <Route path="/settings/alerts" element={<AlertSettingsPage />} />
    <Route path="/import" element={<PlaceholderPage title="Excel / CSV 导入" description="下一阶段将提供字段自动识别与安全映射，不会覆盖已有历史数据。" />} />
    <Route path="/reports" element={<PlaceholderPage title="投放日报" description="后续将根据行情数据生成今日总结、风险计划和明日建议。" />} />
    <Route path="/materials" element={<PlaceholderPage title="素材检测" description="已为巨量违规检测系统保留独立入口。" />} />
    <Route path="*" element={<PlaceholderPage title="页面不存在" description="请从左侧导航返回行情首页。" />} />
  </Routes></div></div>;
}

