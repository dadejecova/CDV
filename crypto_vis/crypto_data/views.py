from django.shortcuts import render
from pycoingecko import CoinGeckoAPI
import datetime

def home(request):
    cg = CoinGeckoAPI()

    # Fetch top 100 cryptocurrencies by market cap
    top_100 = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=100, page=1)
    
    # Extract top 10 for charts
    top_10 = top_100[:10]

    # Bar chart data
    bar_labels = [coin['name'] for coin in top_10]
    bar_data = [coin['current_price'] for coin in top_10]

    historical_data = {}
    for coin in top_10:
        coin_id = coin['id']
        historical = cg.get_coin_market_chart_by_id(id = coin_id, vs_currency='usd', days=7)
        prices = [price[1] for price in historical['prices']][:7]
        historical_data[coin_id] = prices

    today = datetime.date.today()
    dates = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    
    context = {
        'crypto_data': top_100,
        'bar_labels': bar_labels,
        'bar_data': bar_data,
        'historical_data': historical_data,
        'dates': dates,
        'top_10_ids': [coin['id'] for coin in top_10]
    }
    return render(request, 'crypto_data/home.html', context)

def about(request):
    return render(request, 'crypto_data/about.html')