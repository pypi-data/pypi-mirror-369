# ⭐ Telegram Stars Rates

[![PyPI version](https://badge.fury.io/py/telegram-stars-rates.svg)](https://badge.fury.io/py/telegram-stars-rates)
[![Python versions](https://img.shields.io/pypi/pyversions/telegram-stars-rates.svg)](https://pypi.org/project/telegram-stars-rates/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Real-time Telegram Stars to USDT exchange rates via Fragment blockchain analysis**

## 🚀 Features

- **Real-time Exchange Rates**: Get current Stars → USDT rates from Fragment blockchain
- **Minimalistic Library**: Simple Python API with minimal dependencies  
- **CLI Tool**: Command-line interface for quick rate checks
- **Web Converter**: GitHub Pages hosted converter with daily updates
- **Fragment Integration**: Direct blockchain transaction parsing
- **Binance API**: TON → USDT rates from Binance

## 📦 Installation

```bash
pip install telegram-stars-rates
```

## 💻 Usage

### Python API

```python
from telegram_stars_rates import get_stars_rate

# Get current exchange rates
result = get_stars_rate()
print(f"1 Star = ${result['usdt_per_star']:.6f} USDT")
print(f"1000 Stars = ${result['usdt_per_star'] * 1000:.2f} USDT")

# With raw transaction data
result = get_stars_rate(include_raw=True, limit=100)
print(f"Based on {result['fragment_raw']['transactions_count']} transactions")
```

### CLI Tool

```bash
# Basic usage
telegram-stars-rates

# More transactions for better accuracy
telegram-stars-rates --limit 100

# JSON output
telegram-stars-rates --json

# With TON API key (faster, no rate limits)
telegram-stars-rates --api-key YOUR_TON_API_KEY
```

### Web Interface

Visit the GitHub Pages site for an interactive converter:
- Real-time rates updated daily
- Convert between Stars ↔ USDT
- Exchange rate statistics
- Mobile-friendly interface


## 🔧 How It Works

1. **Fragment Analysis**: Fetches real transactions from Fragment's TON address
2. **Rate Calculation**: Parses "X Telegram Stars" → TON transfers  
3. **USDT Conversion**: Gets TON/USDT rate from Binance API
4. **Final Rate**: Calculates Stars → USDT via Stars → TON → USDT

## 📊 API Reference

### `get_stars_rate(limit=50, include_raw=False, **kwargs)`

**Parameters:**
- `limit` (int): Number of transactions to analyze (default: 50)
- `include_raw` (bool): Include raw transaction data (default: False)  
- `api_key` (str): TON API key for higher rate limits

**Returns:**
```python
{
    "usdt_per_star": 0.012345,      # Main exchange rate
    "ton_per_star": 0.002500,       # Stars → TON rate  
    "usdt_per_ton": 4.938000,       # TON → USDT rate
    "timestamp": "2024-01-01T12:00:00Z",
    "errors": []                     # Any warnings/errors
}
```

## 🌍 GitHub Actions Integration

Automated daily updates for GitHub Pages:

```yaml
- name: Update Exchange Rates
  run: |
    python scripts/generate_rates.py
    # Deploys to GitHub Pages automatically
```

## 🛠 Development

```bash
git clone https://github.com/username/telegram-stars-rates
cd telegram-stars-rates
pip install -e .

# Run tests
python -m pytest

# Generate web data
python scripts/generate_rates.py
```

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **Fragment**: https://fragment.com
- **TON API**: https://tonapi.io  
- **Binance API**: https://binance.com/api

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! 

1. Форкните репозиторий
2. Создайте ветку для вашей функции (`git checkout -b feature/amazing-feature`)
3. Сделайте коммит (`git commit -m 'Add amazing feature'`)
4. Пушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📜 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

## 🔗 Ссылки

- **PyPI**: https://pypi.org/project/fragment-stars-analyzer/
- **GitHub**: https://github.com/fragment-stars/analyzer
- **Документация**: https://fragment-stars.readthedocs.io/
- **Баг-репорты**: https://github.com/fragment-stars/analyzer/issues

## 📊 Статистика

![GitHub stars](https://img.shields.io/github/stars/fragment-stars/analyzer)
![GitHub forks](https://img.shields.io/github/forks/fragment-stars/analyzer)
![PyPI downloads](https://img.shields.io/pypi/dm/fragment-stars-analyzer)

---

**💎 Профессиональный анализ Telegram Stars курсов для Python разработчиков! 💎**