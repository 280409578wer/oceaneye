from __future__ import annotations

from typing import Any


class AIService:
    """V0.1 使用规则模板；未来可替换为任意大模型提供商。"""

    def analyze(self, account: dict[str, Any], summary: dict[str, Any], plans: list[dict[str, Any]]) -> str:
        if not plans:
            return "当前暂无计划数据，系统会在收到数据后自动生成分析。"
        best = min((p for p in plans if p.get("cpa") is not None), key=lambda p: p["cpa"], default=None)
        risky = max(plans, key=lambda p: p.get("risk_score", 0))
        cpa_text = "暂无" if summary.get("cpa") is None else f"¥{summary['cpa']:.2f}"
        lines = [
            f"截至最新数据时间，{account['name']}今日消耗 ¥{summary['cost']:.2f}，获得 {summary['conversions']} 个转化，平均 CPA 为 {cpa_text}。"
        ]
        if best:
            lines.append(f"{best['name']}当前效率最好，CPA 为 ¥{best['cpa']:.2f}，建议继续观察其稳定性。")
        if risky.get("status_label") in {"风险", "异常", "观察"}:
            lines.append(f"{risky['name']}当前状态为{risky['status_label']}，{risky['status_reason']}，建议重点关注。")
        else:
            lines.append("各计划暂未出现严重异常，建议保持当前监控节奏。")
        return "\n\n".join(lines)

