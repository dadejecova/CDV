from django.shortcuts import render
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

def home(request):
    # Fetch top 100 cryptocurrencies by market cap
    data = cg.get_coins_markets(vs_currency='usd', per_page=100, page=1)
    # Prepare chart data (top 10 for readability)
    labels = [coin['name'] for coin in data[:10]]
    prices = [coin['current_price'] for coin in data[:10]]
    
    context = {
        'crypto_data': data,
        'chart_labels': labels,
        'chart_data': prices,
    }
    return render(request, 'crypto_data/home.html', context)

def about(request):
    return render(request, 'crypto_data/about.html')