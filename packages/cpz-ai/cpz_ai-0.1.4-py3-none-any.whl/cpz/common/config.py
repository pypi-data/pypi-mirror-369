from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from dotenv import load_dotenv


@dataclass
class Config:
    env: str
    log_level: str
    request_timeout_seconds: int

    @staticmethod
    def from_env(environ: Mapping[str, str]) -> "Config":
        load_dotenv()  # load from .env if present
        env = environ.get("CPZ_ENV", "dev")
        log_level = environ.get("CPZ_LOG_LEVEL", "INFO")
        timeout = int(environ.get("CPZ_REQUEST_TIMEOUT_SECONDS", "30"))
        return Config(env=env, log_level=log_level, request_timeout_seconds=timeout)
