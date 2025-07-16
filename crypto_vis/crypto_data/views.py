from django.shortcuts import render
from pycoingecko import CoinGeckoAPI
from datetime import datetime, timedelta
import concurrent.futures
from django.core.cache import cache # Dunno if are going to continue using this

cg = CoinGeckoAPI()

def fetch_historical_data(coin_id):
    cache_key = f'historical_{coin_id}'
    data = cache.get(cache_key)

    if not data:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        unix_start = int(start_date.timestamp())
        unix_end = int(end_date.timestamp())
        data = cg.get_coin_market_chart_range_by_id(
            id=coin_id,
            vs_currency='usd',
            from_timestamp=unix_start,
            to_timestamp=unix_end
        )
        cache.set(cache_key, data, timeout=600)  # Cache for 10 minutes
    return data

def home(request):
    cache_key_top = 'top_coin'
    top_coins = cache.get(cache_key_top)
    if not top_coins:
        top_coins = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=10, page=1)
        cache.set(cache_key_top, top_coins, timeout=600)
        
        # Sort barchart - descending
        top_coins_sorted = sorted(top_coins, key=lambda x: x['current_price'], reverse=True)

        #barchart
        bar_labels = [coin['name'] for coin in top_coins_sorted]
        bar_prices = [coin['current_price'] for coin in top_coins_sorted]

        coin_colors = {
        'bitcoin': '#F7931A',  # Orange
        'ethereum': '#627EEA',  # Blue
        'tether': '#26A17B',  # Green
        'binancecoin': '#F3BA2F',  # Yellow
        'solana': '#9945FF',  # Purple
        'ripple': '#23292F',  # Dark gray (XRP)
        'usd-coin': '#2775CA',  # Blue
        'staked-ether': '#6B5BFF',  # Light purple (Lido)
        'dogecoin': '#C3A634',  # Gold
        'tron': '#EF0027',  # Red   
    }

    top5 = top_coins[:5]
    historical_data = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_coin = {executor.submit(fetch_historical_data, coin['id']): coin for coin in top5}
        for future in concurrent.futures.as_completed(future_to_coin):
            coin = future_to_coin[future]
            try:
                data = future.result()
                prices = [p[1] for p in data['prices']]
                if prices:
                    base = prices[0]
                    percent_prices = [ (p / base * 100 ) for p in prices ] # normalized
                    historical_data[coin['id']] = percent_prices
                else:
                    historical_data[coin['id']] = []
                    # data take first coin data
                if 'dates' not in historical_data:
                    dates = [datetime.fromtimestamp(p[0] / 1000).strftime('%Y-%m-%d') for p in data['prices']]
                    historical_data['dates'] = dates
            except Exception as e:
                historical_data[coin['id']] = []
            

    context = {
        'bar_labels': bar_labels,
        'bar_prices': bar_prices,
        'historical_data': historical_data,
        'top_coins': top_coins,
        'coin_colors': coin_colors,
    }
    return render(request, 'crypto_data/home.html', context)