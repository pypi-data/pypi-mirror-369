from __future__ import annotations

import os
from typing import Any, Mapping, Optional

import requests

from .logging import get_logger


class SupabaseClient:
    def __init__(self, url: str, anon_key: str, service_key: Optional[str] = None) -> None:
        self.url = url.rstrip("/")
        self.anon_key = anon_key
        self.service_key = service_key or anon_key
        self.logger = get_logger()

    @staticmethod
    def from_env(environ: Optional[Mapping[str, str]] = None) -> "SupabaseClient":
        env = environ or os.environ
        url = env.get("SUPABASE_URL", "")
        anon = env.get("SUPABASE_ANON_KEY", "")
        service = env.get("SUPABASE_SERVICE_ROLE_KEY", None)
        return SupabaseClient(url=url, anon_key=anon, service_key=service)

    def _headers(self) -> dict[str, str]:
        return {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.service_key}",
        }

    def health(self) -> bool:
        try:
            resp = requests.get(self.url, timeout=10)
            return resp.status_code < 500
        except Exception as exc:  # noqa: BLE001
            self.logger.error("supabase_health_error", error=str(exc))
            return False

    def list_tables(self) -> list[str]:
        # Query information_schema via RPC if PostgREST enabled; fallback to empty
        try:
            # PostgREST introspection is restricted; attempt a lightweight table query
            resp = requests.get(f"{self.url}/rest/v1/", headers=self._headers(), timeout=10)
            if resp.status_code == 200 and isinstance(resp.json(), dict):
                return sorted(resp.json().keys())
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("supabase_list_tables_error", error=str(exc))
        return []

    def echo(self) -> dict[str, Any]:
        try:
            resp = requests.get(f"{self.url}/rest/v1/", headers=self._headers(), timeout=10)
            return {"status": resp.status_code, "ok": resp.ok}
        except Exception as exc:  # noqa: BLE001
            return {"status": 0, "ok": False, "error": str(exc)}
