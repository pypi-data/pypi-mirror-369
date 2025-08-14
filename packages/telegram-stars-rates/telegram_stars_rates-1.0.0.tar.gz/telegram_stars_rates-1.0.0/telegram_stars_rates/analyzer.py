#!/usr/bin/env python3
"""
⭐ Telegram Stars Rates
Real-time Telegram Stars to USDT exchange rates via Fragment blockchain
"""

import requests
import time
import re
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

def get_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()

def ton_to_usdt_binance() -> Dict[str, Any]:
    """Get TON → USDT exchange rate from Binance API."""
    try:
        response = requests.get(
            "https://api.binance.com/api/v3/ticker/price?symbol=TONUSDT",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if "price" in data and float(data["price"]) > 0:
            return {
                "usdt_per_ton": float(data["price"]),
                "last_updated": get_timestamp(),
                "source": "binance"
            }
    except:
        pass
    return {}

def parse_fragment_transaction(transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse Fragment Stars → TON transaction."""
    try:
        for action in transaction.get("actions", []):
            if action.get("type") == "TonTransfer":
                transfer = action.get("TonTransfer", {})
                comment = transfer.get("comment", "")
                
                stars_match = re.search(r'(\d+)\s+Telegram\s+Stars', comment)
                if not stars_match:
                    continue
                
                stars = int(stars_match.group(1))
                ton_amount = int(transfer.get("amount", 0)) / 1_000_000_000
                
                if stars > 0 and ton_amount > 0:
                    ref_match = re.search(r'Ref#(\w+)', comment)
                    return {
                        "timestamp": transaction.get("timestamp", 0),
                        "stars": stars,
                        "ton": ton_amount,
                        "rate_per_star": ton_amount / stars,
                        "reference": ref_match.group(1) if ref_match else "Unknown",
                        "hash": transaction.get("event_id", "")
                    }
    except:
        pass
    return None

def get_fragment_events(
    limit: int = 50,
    fragment_address: str = "EQCFJEP4WZ_mpdo0_kMEmsTgvrMHG7K_tWY16pQhKHwoOoy2",
    rate_limit_delay: float = 2.0,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get Fragment account events via TON API."""
    if not api_key:
        time.sleep(rate_limit_delay)
    
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    
    response = requests.get(
        f"https://tonapi.io/v2/accounts/{fragment_address}/events",
        params={"limit": limit},
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 429:
        time.sleep(7)
        return get_fragment_events(limit, fragment_address, rate_limit_delay, api_key)
    
    response.raise_for_status()
    return response.json().get("events", [])

def stars_to_ton_fragment(
    limit: int = 50,
    fragment_address: str = "EQCFJEP4WZ_mpdo0_kMEmsTgvrMHG7K_tWY16pQhKHwoOoy2",
    rate_limit_delay: float = 2.0,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Get current Stars → TON exchange rates via Fragment."""
    events = get_fragment_events(limit, fragment_address, rate_limit_delay, api_key)
    
    stars_txs = []
    for event in events:
        if result := parse_fragment_transaction(event):
            stars_txs.append(result)
    
    if not stars_txs:
        raise Exception("No Stars transactions found")
    
    rates = [tx['rate_per_star'] for tx in stars_txs if 0 < tx['rate_per_star'] <= 1]
    
    if not rates:
        raise Exception("No valid rates found")
    
    return {
        "ton_per_star": sum(rates) / len(rates),
        "transactions_count": len(stars_txs),
        "min_rate": min(rates),
        "max_rate": max(rates),
        "median_rate": sorted(rates)[len(rates)//2],
        "timestamp": get_timestamp(),
        "raw_transactions": stars_txs
    }

def get_stars_rate(limit: int = 50, include_raw: bool = False, **kwargs) -> Dict[str, Any]:
    """Get complete Stars → TON → USDT exchange rate."""
    errors = []
    timestamp = get_timestamp()
    
    # Get Stars → TON rates
    try:
        stars_to_ton = stars_to_ton_fragment(limit=limit, **kwargs)
        ton_per_star = stars_to_ton.get("ton_per_star", -1)
        if ton_per_star <= 0:
            errors.append("Invalid Stars→TON rate")
            ton_per_star = -1
    except Exception as e:
        errors.append(f"Fragment error: {e}")
        stars_to_ton = {}
        ton_per_star = -1
    
    # Get TON → USDT rates
    try:
        ton_to_usdt = ton_to_usdt_binance()
        usdt_per_ton = ton_to_usdt.get("usdt_per_ton", -1)
        if usdt_per_ton <= 0:
            errors.append("Invalid TON→USDT rate")
            usdt_per_ton = -1
    except Exception as e:
        errors.append(f"Binance error: {e}")
        ton_to_usdt = {}
        usdt_per_ton = -1
    
    # Calculate final rate
    if ton_per_star > 0 and usdt_per_ton > 0:
        usdt_per_star = ton_per_star * usdt_per_ton
        if usdt_per_star > 10 or usdt_per_star < 0.0001:
            errors.append(f"Suspicious rate: ${usdt_per_star:.6f}")
    else:
        usdt_per_star = -1
        if not errors:
            errors.append("No exchange rates available")
    
    result = {
        "ton_per_star": ton_per_star,
        "usdt_per_ton": usdt_per_ton,
        "usdt_per_star": usdt_per_star,
        "timestamp": timestamp,
        "errors": errors
    }
    
    if include_raw:
        result["fragment_raw"] = stars_to_ton
        result["binance_raw"] = ton_to_usdt
    
    return result

if __name__ == "__main__":
    import json
    result = get_stars_rate(include_raw=True)
    print(json.dumps(result, indent=2))
    
    if result["usdt_per_star"] > 0:
        print(f"\n1 Star = ${result['usdt_per_star']:.6f} USDT")
        print(f"1000 Stars = ${result['usdt_per_star'] * 1000:.2f} USDT")
