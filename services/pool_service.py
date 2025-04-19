# services/pool_service.py

import requests
import logging

logger = logging.getLogger(__name__)

def fetch_pools(limit=5, offset=0):
    url = f"https://dlmm-api.meteora.ag/pair/all_with_pagination?limit={limit}&offset={offset}"
    try:
        response = requests.get(url)
        data = response.json()
        pairs = data.get("pairs", [])
        total = data.get("total_count", 0)

        if not pairs:
            return "❌ No liquidity pools found.", 0, total

        msg = f"🌊 Pools on Meteora ({offset+1}-{offset+len(pairs)} of {total}):\n"
        for p in pairs:
            name = p.get("name", "N/A")
            liquidity = float(p.get("liquidity") or 0)
            price = float(p.get("current_price") or 0)
            volume = float(p.get("trade_volume_24h") or 0)
            msg += (
                f"\n🔹 Pool: {name}\n"
                f"💰 TVL: ${liquidity:,.2f}\n"
                f"💱 Price: ${price:,.2f}\n"
                f"📈 Volume (24h): ${volume:,.2f}\n"
            )
        return msg, len(pairs), total

    except Exception as e:
        logger.error(f"Error fetching pools: {e}")
        return f"❌ Error fetching data: {e}", 0, 0

def search_pool(pool_name):
    url = "https://dlmm-api.meteora.ag/pair/all_with_pagination"
    params = {
        "search_term": pool_name,
        "limit": 100,
        "include_unknown": "true"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        pairs = data.get("pairs", [])

        exact = next((p for p in pairs if p.get("name") == pool_name), None)
        if not exact:
            return f"❌ No pools found matching '{pool_name}'."

        liquidity = float(exact.get("liquidity") or 0)
        price = float(exact.get("current_price") or 0)
        volume = float(exact.get("trade_volume_24h") or 0)
        fees = float(exact.get("fee") or 0)

        return (
            f"📊 Pool Details: {exact['name']}\n\n"
            f"💰 TVL: ${liquidity:,.2f}\n"
            f"💱 Current Price: ${price:,.6f}\n"
            f"📈 Volume (24h): ${volume:,.2f}\n"
            f"💸 Fee: {fees * 100:.2f}%\n"
        )

    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return "❌ Network error while searching for pool."
    except Exception as e:
        logger.error(f"Parsing error: {e}")
        return "❌ Error processing pool data."
