"""
⭐ Telegram Stars Rates
Real-time Telegram Stars to USDT exchange rates via Fragment blockchain
"""

from .analyzer import get_stars_rate, stars_to_ton_fragment, ton_to_usdt_binance

__version__ = "1.0.0"
__all__ = ["get_stars_rate", "stars_to_ton_fragment", "ton_to_usdt_binance"]