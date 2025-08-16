from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass
class AlpacaAuth:
    api_key_id: str
    api_secret_key: str
    env: str  # "paper" | "live"

    @staticmethod
    def from_env(environ: Mapping[str, str]) -> "AlpacaAuth":
        return AlpacaAuth(
            api_key_id=environ.get("ALPACA_API_KEY_ID", ""),
            api_secret_key=environ.get("ALPACA_API_SECRET_KEY", ""),
            env=environ.get("ALPACA_ENV", "paper"),
        )
