<a href="https://www.cpz-lab.com/">
  <img src="https://drive.google.com/uc?id=1JY-PoPj9GHmpq3bZLC7WyJLbGuT1L3hN" alt="CPZ Lab" width="150">
</a>
# CPZ AI — Python SDK

[![CI](https://github.com/CPZ-Lab/cpz-py/actions/workflows/ci.yml/badge.svg)](https://github.com/CPZ-Lab/cpz-py/actions)
[![Coverage](https://img.shields.io/badge/coverage-85%25%2B-brightgreen.svg)](https://github.com/CPZ-Lab/cpz-py)
[![Python](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue.svg)](https://www.python.org/)

## Install

```bash
pip install cpz-ai
# dev
pip install -e .[dev]
```

## 60-second Quickstart (Sync)

```python
import cpz
from cpz.execution.models import OrderSubmitRequest
from cpz.execution.enums import OrderSide, OrderType, TimeInForce

client = cpz.clients.sync.CPZClient()
client.execution.use_broker("alpaca", env="paper")

order = client.execution.submit_order(OrderSubmitRequest(
    symbol="AAPL",
    side=OrderSide.BUY,
    qty=10,
    type=OrderType.MARKET,
    time_in_force=TimeInForce.DAY,
))
print(order.id, order.status)
```

## Execution Architecture

```
CPZClient.execution  -->  BrokerRouter  -->  AlpacaAdapter
                              |               ^
                              +---- future brokers (IBKR, Tradier, ...)
```

## Configuration (.env)

| Key | Description | Example | Required |
| --- | --- | --- | --- |
| CPZ_ENV | SDK environment | dev | No |
| CPZ_LOG_LEVEL | Log level | INFO | No |
| CPZ_REQUEST_TIMEOUT_SECONDS | Default request timeout | 30 | No |
| ALPACA_ENV | Alpaca environment | paper | Yes (if using Alpaca) |
| ALPACA_API_KEY_ID | Alpaca API key | AK... | Yes (if using Alpaca) |
| ALPACA_API_SECRET_KEY | Alpaca API secret | ... | Yes (if using Alpaca) |

## Usage

### Selecting a broker
```python
client.execution.use_broker("alpaca", env="paper")
```

### Submit / cancel / replace order (sync)
```python
from cpz.execution.models import OrderSubmitRequest, OrderReplaceRequest
from cpz.execution.enums import OrderSide, OrderType, TimeInForce

req = OrderSubmitRequest(symbol="AAPL", side=OrderSide.BUY, qty=1,
                         type=OrderType.MARKET, time_in_force=TimeInForce.DAY)
order = client.execution.submit_order(req)
client.execution.cancel_order(order.id)
client.execution.replace_order(order.id, OrderReplaceRequest(qty=2))
```

### Async + Streaming
```python
import asyncio
from cpz.clients.async_ import AsyncCPZClient

async def main():
    client = AsyncCPZClient()
    await client.execution.use_broker("alpaca", env="paper")
    async for q in client.execution.stream_quotes(["AAPL", "MSFT"]):
        print(q.symbol, q.bid, q.ask)
        break

asyncio.run(main())
```

### Get account / positions
```python
acct = client.execution.get_account()
positions = client.execution.get_positions()
```

### CLI
```bash
cpz-ai broker list
cpz-ai broker use alpaca --env paper
cpz-ai order submit --symbol AAPL --side buy --qty 10 --type market --tif day
cpz-ai order get --id <id>
cpz-ai positions
cpz-ai stream quotes --symbols AAPL,MSFT
```

## Error handling

Catch `cpz.common.errors.CPZBrokerError`. Broker errors are mapped to CPZ errors.

## Logging & Redaction

Structured JSON logging via `structlog`, with redaction of `Authorization`, `ALPACA_API_SECRET_KEY`, and similar.
Configure level via `CPZ_LOG_LEVEL`.

## Testing & Quality

- `make test` (coverage goal ≥ 85%)
- `mypy --strict`

## Contributing

Style: ruff/black/isort, pre-commit, branch naming. See `CONTRIBUTING.md`.

## Versioning & Release

Bump version in `pyproject.toml`, build, and publish to PyPI.

## Roadmap

Next brokers: IBKR, Tradier, …

## Security

See `SECURITY.md`. No LICENSE file is included intentionally.
