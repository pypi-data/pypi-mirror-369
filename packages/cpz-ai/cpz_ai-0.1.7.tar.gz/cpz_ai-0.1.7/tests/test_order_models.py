from __future__ import annotations

import pytest

from cpz.execution.enums import OrderSide, OrderType, TimeInForce
from cpz.execution.models import OrderSubmitRequest


def test_limit_order_requires_price() -> None:
    with pytest.raises(ValueError):
        OrderSubmitRequest(
            symbol="AAPL",
            side=OrderSide.BUY,
            qty=1,
            type=OrderType.LIMIT,
            time_in_force=TimeInForce.DAY,
        )


def test_market_order_no_price_ok() -> None:
    req = OrderSubmitRequest(
        symbol="AAPL",
        side=OrderSide.BUY,
        qty=1,
        type=OrderType.MARKET,
        time_in_force=TimeInForce.DAY,
    )
    assert req.symbol == "AAPL"
