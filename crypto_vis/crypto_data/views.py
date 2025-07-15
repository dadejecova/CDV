from django.shortcuts import render
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

def home(request):
    # To fetch the top 5
    data = cg.get_coins_markets(vs_currency='usd', per_page=100, page=1)
    labels = [coin['name'] for coin in data]
    prices = [coin['current_price'] for coin in data]
    context = {
        'crypto_data': data, # Full data for rendering
        'chart_labels': labels, # Labels for the chart
        'chart_prices': prices, # Prices for the chart
    }
    return render(request, 'crypto_data/home.html', context)