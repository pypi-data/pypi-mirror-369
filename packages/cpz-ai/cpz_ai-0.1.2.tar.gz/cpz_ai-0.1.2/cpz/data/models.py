from __future__ import annotations

from pydantic import BaseModel


class Bar(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
