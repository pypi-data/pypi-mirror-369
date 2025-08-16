from __future__ import annotations

from pydantic import BaseModel


class Strategy(BaseModel):
    name: str
