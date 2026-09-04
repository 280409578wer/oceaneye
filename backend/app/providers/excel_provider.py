from .base import DataProvider


class ExcelProvider(DataProvider):
    """Excel/CSV 导入提供者占位，V0.1 首页不依赖此模块。"""

    def _unavailable(self):
        raise NotImplementedError("Excel/CSV 字段映射将在后续阶段启用")

    get_accounts = get_account_summary = get_plans = get_plan_metrics = get_timeseries = get_balance = _unavailable

