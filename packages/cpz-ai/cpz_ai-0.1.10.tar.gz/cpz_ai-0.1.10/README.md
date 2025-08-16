<a href="https://www.cpz-lab.com/">
  <img src="https://drive.google.com/uc?id=1JY-PoPj9GHmpq3bZLC7WyJLbGuT1L3hN" alt="CPZ Lab" width="150">
</a>

# CPZ AI — Python SDK

[![Coverage](https://img.shields.io/badge/coverage-85%25%2B-brightgreen.svg)](https://github.com/CPZ-Lab/cpz-py)
[![Python](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue.svg)](https://www.python.org/)

## Install

```bash
pip install cpz-ai
```

## 60-second Quickstart (Sync)

### Trading
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
| CPZ_AI_URL | CPZ AI API Endpoint | https://api.cpz-lab.com/cpz-ai/v1 | No |
| CPZ_AI_API_KEY | CPZ AI API Key | sb_publishable_... | Yes (for platform access) |
| CPZ_AI_SECRET_KEY | CPZ AI Secret Key | sb_secret_... | Yes (for platform access) |
| CPZ_AI_USER_ID | CPZ AI User ID | user123 | Yes (for user-specific access) |
| CPZ_AI_IS_ADMIN | CPZ AI Admin Access | false | No (set to true for admin) |

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

### CPZ AI - Strategies & Files

Access your CPZ AI platform data including strategies and files:

```python
from cpz.common.cpz_ai import CPZAIClient

# Connect to CPZ AI
client = CPZAIClient.from_env()

# Get your strategies (user-specific by default)
strategies = client.get_strategies()
print(f"Your strategies: {[s.get('title', 'Unknown') for s in strategies]}")

# Create a new strategy (automatically assigned to your user_id)
new_strategy = client.create_strategy({
    "title": "My Trading Bot",
    "description": "Automated trading strategy",
    "strategy_type": "momentum",
    "status": "active"
})
```

#### User-Specific Access Control

The CPZ AI client automatically handles user isolation:

- **Regular Users**: Only see and manage their own strategies and files
- **Admins**: Can access all strategies and files across all users

```python
# Regular user client (user-specific access)
user_client = CPZAIClient(
    url="https://api.cpz-lab.com",
    api_key="your_api_key",
    secret_key="your_secret_key",
    user_id="user123",
    is_admin=False
)

# Admin client (full access)
admin_client = CPZAIClient(
    url="https://api.cpz-lab.com",
    api_key="admin_api_key",
    secret_key="admin_secret_key",
    user_id=None,
    is_admin=True
)

# Environment variables for automatic configuration
# CPZ_AI_USER_ID=user123
# CPZ_AI_IS_ADMIN=false
```

#### File Operations & DataFrames

Upload, download, and manage files with pandas DataFrame support:

```python
import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({
    'symbol': ['AAPL', 'GOOGL', 'MSFT'],
    'price': [150.25, 2750.80, 310.45],
    'volume': [1000000, 500000, 800000]
})

# Upload DataFrame as CSV
client.upload_dataframe("data-bucket", "stocks.csv", df, format="csv")

# Upload DataFrame as JSON
client.upload_dataframe("data-bucket", "stocks.json", df, format="json")

# Upload DataFrame as Parquet
client.upload_dataframe("data-bucket", "stocks.parquet", df, format="parquet")

# Download CSV and load to DataFrame
downloaded_df = client.download_csv_to_dataframe("data-bucket", "stocks.csv")

# Download JSON and load to DataFrame
downloaded_df = client.download_json_to_dataframe("data-bucket", "stocks.json")

# Download Parquet and load to DataFrame
downloaded_df = client.download_parquet_to_dataframe("data-bucket", "stocks.parquet")

# List files in a bucket
files = client.list_files_in_bucket("data-bucket", prefix="stocks")

# Delete files
client.delete_file("data-bucket", "stocks.csv")
```

#### Load User Strategies to DataFrame

```python
from cpz.common.cpz_ai import CPZAIClient
import pandas as pd

# Load strategies for a specific user
client = CPZAIClient(
    url="https://api.cpz-lab.com",
    api_key="your_api_key",
    secret_key="your_secret_key",
    user_id="user-uuid-here",
    is_admin=False
)

# Get user's strategies as DataFrame
strategies_df = pd.DataFrame(client.get_strategies())
print(f"Found {len(strategies_df)} strategies")
print(strategies_df.head())
```

**Note**: The CPZ AI client connects to your API endpoint at `api.cpz-lab.com`. Users only need to provide their CPZ AI API keys.



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

## Python Compatibility

This package is tested and compatible with:
- **Python 3.9** ✅
- **Python 3.10** ✅  
- **Python 3.11** ✅
- **Python 3.12** ✅

### Compatibility Features
- Uses `from __future__ import annotations` for forward-compatible type hints
- Compatible type annotation syntax across all supported versions
- No version-specific syntax that would break older Python versions
- Continuous integration testing on all supported Python versions

## Contributing

Style: ruff/black/isort, pre-commit, branch naming. See `CONTRIBUTING.md`.

## Versioning & Release

Bump version in `pyproject.toml`, build, and publish to PyPI.

## Roadmap

Next brokers: IBKR, Tradier, …

## Security

See `SECURITY.md`. No LICENSE file is included intentionally.
