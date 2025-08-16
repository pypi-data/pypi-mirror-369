from __future__ import annotations

import os
from typing import AsyncIterator, Callable, Dict, Iterable, Optional

from ..common.errors import BrokerNotRegistered
from .interfaces import BrokerAdapter
from .models import Account, Order, OrderReplaceRequest, OrderSubmitRequest, Position, Quote

BROKER_ALPACA = "alpaca"


class BrokerRouter:
    _registry: Dict[str, Callable[..., BrokerAdapter]] = {}

    def __init__(self) -> None:
        self._active: Optional[BrokerAdapter] = None

    @classmethod
    def register(cls, name: str, factory: Callable[..., BrokerAdapter]) -> None:
        cls._registry[name] = factory

    def list_brokers(self) -> list[str]:
        return list(self._registry.keys())

    @classmethod
    def default(cls) -> "BrokerRouter":
        if BROKER_ALPACA not in cls._registry:
            try:
                from .alpaca.adapter import AlpacaAdapter

                cls.register(BROKER_ALPACA, AlpacaAdapter.create)
            except Exception:
                pass
        return cls()

    def use_broker(self, name: str, **kwargs: object) -> None:
        if name not in self._registry:
            raise BrokerNotRegistered(name)
        factory = self._registry[name]
        self._active = factory(**kwargs)

    def _require_active(self) -> BrokerAdapter:
        if self._active is None:
            if len(self._registry) == 1:
                _name, factory = next(iter(self._registry.items()))
                self._active = factory()
                return self._active
            if os.getenv("ALPACA_API_KEY_ID"):
                self.use_broker(BROKER_ALPACA, env=os.getenv("ALPACA_ENV", "paper"))
            else:
                raise BrokerNotRegistered("<none>")
        assert self._active is not None
        return self._active

    def get_account(self) -> Account:
        return self._require_active().get_account()

    def get_positions(self) -> list[Position]:
        return self._require_active().get_positions()

    def submit_order(self, req: OrderSubmitRequest) -> Order:
        return self._require_active().submit_order(req)

    def get_order(self, order_id: str) -> Order:
        return self._require_active().get_order(order_id)

    def cancel_order(self, order_id: str) -> Order:
        return self._require_active().cancel_order(order_id)

    def replace_order(self, order_id: str, req: OrderReplaceRequest) -> Order:
        return self._require_active().replace_order(order_id, req)

    def stream_quotes(self, symbols: Iterable[str]) -> AsyncIterator[Quote]:
        active = self._require_active()
        return active.stream_quotes(symbols)
