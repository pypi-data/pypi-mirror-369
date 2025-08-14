# 🚀 Installation

## Quick Install

```bash
pip install telegram-stars-rates
```

## From Source

```bash
git clone https://github.com/username/telegram-stars-rates
cd telegram-stars-rates
pip install -e .
```

## Usage

```python
from telegram_stars_rates import get_stars_rate

result = get_stars_rate()
print(f"1 Star = ${result['usdt_per_star']:.6f} USDT")
```

## CLI Usage

```bash
telegram-stars-rates --limit 50
telegram-stars-rates --json
```

## Requirements

- Python 3.7+
- requests>=2.25.0