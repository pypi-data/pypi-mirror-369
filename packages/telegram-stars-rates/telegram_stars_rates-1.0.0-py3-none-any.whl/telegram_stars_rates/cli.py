#!/usr/bin/env python3
"""
⭐ Telegram Stars Rates - Minimalistic CLI
"""

import sys
import json
import argparse
from .analyzer import get_stars_rate


def main():
    """Minimalistic CLI for Telegram Stars Rates"""
    parser = argparse.ArgumentParser(
        description="⭐ Telegram Stars → USDT Exchange Rates",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--limit", type=int, default=50, help="Number of transactions to analyze")
    parser.add_argument("--raw", action="store_true", help="Include raw data")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--api-key", help="TON API key")
    
    args = parser.parse_args()
    
    try:
        result = get_stars_rate(
            limit=args.limit,
            include_raw=args.raw,
            api_key=args.api_key
        )
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            usdt_per_star = result["usdt_per_star"]
            if usdt_per_star > 0:
                print(f"1 Star = ${usdt_per_star:.6f} USDT")
                print(f"1000 Stars = ${usdt_per_star * 1000:.2f} USDT")
            else:
                print("❌ Could not get exchange rate")
                if result.get("errors"):
                    for error in result["errors"]:
                        print(f"  • {error}")
                return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())