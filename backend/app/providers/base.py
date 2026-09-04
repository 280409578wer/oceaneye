from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DataProvider(ABC):
    @abstractmethod
    def get_accounts(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def get_account_summary(self, account_id: int) -> dict[str, Any]: ...

    @abstractmethod
    def get_plans(self, account_id: int) -> list[dict[str, Any]]: ...

    @abstractmethod
    def get_plan_metrics(self, plan_id: int) -> dict[str, Any]: ...

    @abstractmethod
    def get_timeseries(self, entity_id: int, interval: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def get_balance(self, account_id: int) -> float: ...

