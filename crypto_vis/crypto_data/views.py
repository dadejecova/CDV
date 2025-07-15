from django.shortcuts import render
from django.core.cache import cache
from pycoingecko import CoinGeckoAPI
import concurrent.futures
import datetime

def home(request):
    cg = CoinGeckoAPI()

    # Cache key for top 10 data
    cache_key_top10 = 'top_10_crypto'
    cache_key_historical = 'historical_data_top5'

    # Fetch top 10 cryptocurrencies (cached for 10 minutes)
    top_10 = cache.get(cache_key_top10)
    if not top_10:
        top_10 = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=10, page=1)
        cache.set(cache_key_top10, top_10, 600)  # Cache for 10 minutes

    # Bar chart data (top 10)
    bar_labels = [coin['name'] for coin in top_10]
    bar_data = [coin['current_price'] for coin in top_10]

    # Fetch historical data concurrently for top 5 (cached for 10 minutes)
    historical_data = cache.get(cache_key_historical)
    if not historical_data:
        historical_data = {}
        top_5_ids = [coin['id'] for coin in top_10[:5]]

        def fetch_hist(coin_id):
            hist = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days=7)
            return coin_id, [point[1] for point in hist['prices']][:7]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fetch_hist, coin_id) for coin_id in top_5_ids]
            for future in concurrent.futures.as_completed(futures):
                coin_id, prices = future.result()
                historical_data[coin_id] = prices

        cache.set(cache_key_historical, historical_data, 600)  # Cache for 10 minutes

    # Dates for x-axis
    today = datetime.date.today()
    dates = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]

    context = {
        'crypto_data': top_10,  # Only top 10 now
        'bar_labels': bar_labels,
        'bar_data': bar_data,
        'historical_data': historical_data,
        'dates': dates,
        'top_5_ids': [coin['id'] for coin in top_10[:5]]  # For line chart
    }
    return render(request, 'crypto_data/home.html', context)