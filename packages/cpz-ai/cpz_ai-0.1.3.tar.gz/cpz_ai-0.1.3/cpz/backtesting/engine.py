from __future__ import annotations

from .models import BacktestResult


def run_stub() -> BacktestResult:
    return BacktestResult(pnl=0.0)
