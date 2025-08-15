# Fragment API Python Client

Python client for [Fragment API](https://fragment-api.net) - Telegram Stars, Premium and TON service.

## Features

- Full Fragment API support
- Session management (auto-save auth_key)
- Detailed error handling
- Support for all operations:
  - Telegram Stars
  - Telegram Premium
  - TON transfers
- Automatic session save/load

## Installation

```bash
pip install fragment-api-py
```

## Quick Start

```python
from FragmentAPI import FragmentAPI, FragmentAuth

# Initialize API
api = FragmentAPI("https://fragment-api.net")

# Authenticate
auth = FragmentAuth(api)
session = auth.create_auth_key("your_cookies", "your_seed")

# Get balance
print(api.general().get_balance())
```

[View full documentation on GitHub](https://github.com/S1qwy/fragment-api-py)