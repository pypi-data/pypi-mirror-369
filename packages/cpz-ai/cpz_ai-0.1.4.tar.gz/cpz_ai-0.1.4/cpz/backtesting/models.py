from __future__ import annotations

from pydantic import BaseModel


class BacktestResult(BaseModel):
    pnl: float
