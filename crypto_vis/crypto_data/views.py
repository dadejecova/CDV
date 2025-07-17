import json
from django.shortcuts import render, redirect
from pycoingecko import CoinGeckoAPI
from .forms import PortfolioForm
from .models import Portfolio
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
    cache_key_top = 'top_coins'
    top_coins = cache.get(cache_key_top)
    if not top_coins:
        top_coins = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=10, page=1)
        cache.set(cache_key_top, top_coins, timeout=600)

    top_coins_sorted = sorted(top_coins, key=lambda x: x['current_price'], reverse=True)

    bar_labels = [coin['name'] for coin in top_coins_sorted]
    bar_prices = [coin['current_price'] for coin in top_coins_sorted]

    coin_colors = {
        'bitcoin': '#F7931A',
        'ethereum': '#627EEA',
        'tether': '#26A17B',
        'binancecoin': '#F3BA2F',
        'solana': '#9945FF',
        'ripple': '#23292F',
        'usd-coin': '#2775CA',
        'staked-ether': '#6B5BFF',
        'dogecoin': '#C3A634',
        'tron': '#EF0027',
    }

    # Sequential fetching for debugging
    top5 = top_coins[:5]
    historical_data = {}
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    unix_start = int(start_date.timestamp())
    unix_end = int(end_date.timestamp())
    dates = None
    for coin in top5:
        cache_key = f'historical_{coin["id"]}'
        data = cache.get(cache_key)
        if not data:
            data = cg.get_coin_market_chart_range_by_id(
                id=coin['id'],
                vs_currency='usd',
                from_timestamp=unix_start,
                to_timestamp=unix_end
            )
            cache.set(cache_key, data, timeout=600)
        prices = [p[1] for p in data['prices']]
        if prices:
            base = prices[0]
            percent_prices = [(p / base * 100) for p in prices]
            historical_data[coin['id']] = percent_prices
        else:
            historical_data[coin['id']] = []
        if dates is None:
            dates = [datetime.fromtimestamp(p[0]/1000).strftime('%Y-%m-%d') for p in data['prices']]
    historical_data['dates'] = dates or []

    context = {
        'bar_labels_json': json.dumps(bar_labels),
        'bar_prices_json': json.dumps(bar_prices),
        'historical_data_json': json.dumps(historical_data),
        'coin_colors_json': json.dumps(coin_colors),
        'top_coins_json': json.dumps(top_coins),
        'top_coins': top_coins,
    }
    return render(request, 'home.html', context)

def portfolio(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('portfolio')
    else:
        form = PortfolioForm()

    # Fetch all holdings (global for now) and calculate values
    holdings = Portfolio.objects.all()
    total_value = 0
    for holding in holdings:
        try:
            price = cg.get_price(ids=holding.coin_id, vs_currencies='usd')[holding.coin_id]['usd']
            holding.current_value = holding.amount * price
            total_value += holding.current_value
        except:
            holding.current_value = 'N/A'  # If API fails for a coin

    context = {
        'form': form,
        'holdings': holdings,
        'total_value': total_value,
    }
    return render(request, 'portfolio.html', context)