from .base import DataProvider


class OceanEngineProvider(DataProvider):
    """真实巨量接口占位。

    V0.1 不编造接口地址或鉴权字段；接入时必须以当前官方文档为准。
    """

    def _unavailable(self):
        raise NotImplementedError("尚未配置真实巨量 API，请使用 DATA_SOURCE=mock")

    get_accounts = get_account_summary = get_plans = get_plan_metrics = get_timeseries = get_balance = _unavailable

