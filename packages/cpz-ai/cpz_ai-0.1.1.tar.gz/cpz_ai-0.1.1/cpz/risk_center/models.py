from __future__ import annotations

from pydantic import BaseModel


class RiskLimit(BaseModel):
    name: str
    value: float
