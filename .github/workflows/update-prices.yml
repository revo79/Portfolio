#!/usr/bin/env python3
import os, json, re, urllib.request, urllib.parse
from datetime import datetime

API_KEY = os.environ.get('FMP_KEY', '')

TICKERS = [
    "AMZN","BAS.DE","BAYN.DE","BMW.DE","HLAG.DE","HEIG.DE",
    "KHC","LHA.DE","NVO","PFE","RWE.DE","NFLX","SPOT","CMCSA",
    "IWDA.AS","GDX","XMEA.DE","SUOE.DE","QDVE.DE","EIMI.DE"
]

STOCK_TICKERS = [
    "AMZN","BAS.DE","BAYN.DE","BMW.DE","HLAG.DE","HEIG.DE",
    "KHC","LHA.DE","NVO","PFE","RWE.DE","NFLX","SPOT","CMCSA"
]

def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  Error: {e}")
        return None

def fetch_prices(tickers):
    results = {}
    for i in range(0, len(tickers), 10):
        chunk = tickers[i:i+10]
        url = f"https://financialmodelingprep.com/api/v3/quote/{','.join(chunk)}?apikey={API_KEY}"
        data = fetch(url)
        if data:
            for item in data:
                results[item['symbol']] = {
                    'price': item.get('price', 0),
                    'change': item.get('changesPercentage', 0),
                    'currency': item.get('currency', ''),
                }
    return results

def fetch_fundamentals(tickers):
    results = {}
    for ticker in tickers:
        print(f"  {ticker}")
        entry = {}
        # Profile: PE, MarketCap
        p = fetch(f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={API_KEY}")
        if p and len(p) > 0:
            entry['pe'] = p[0].get('pe')
            entry['marketCap'] = p[0].get('mktCap')
        # Analyst ratings
        r = fetch(f"https://financialmodelingprep.com/api/v3/analyst-stock-recommendations/{ticker}?limit=1&apikey={API_KEY}")
        if r and len(r) > 0:
            buy  = (r[0].get('analystRatingsStrongBuy') or 0) + (r[0].get('analystRatingsBuy') or 0)
            hold = r[0].get('analystRatingsHold') or 0
            sell = (r[0].get('analystRatingsSell') or 0) + (r[0].get('analystRatingsStrongSell') or 0)
            entry['buy'] = buy; entry['hold'] = hold; entry['sell'] = sell
            total = buy + hold + sell
            if total > 0:
                if buy/total > 0.75: entry['rating'] = 'Strong Buy'
                elif buy/total > 0.5: entry['rating'] = 'Buy'
                elif sell/total > 0.75: entry['rating'] = 'Strong Sell'
                elif sell/total > 0.5: entry['rating'] = 'Sell'
                else: entry['rating'] = 'Halten'
        # Income
        inc = fetch(f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=1&apikey={API_KEY}")
        if inc and len(inc) > 0:
            entry['revenue'] = inc[0].get('revenue')
            entry['netIncome'] = inc[0].get('netIncome')
        if entry:
            results[ticker] = entry
    return results

def fetch_earnings(tickers):
    results = {}
    for ticker in tickers:
        data = fetch(f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{ticker}?limit=5&apikey={API_KEY}")
        if data:
            results[ticker] = [{'date': i.get('date',''), 'label': i.get('fiscalDateEnding', i.get('date','')), 'actual': i.get('eps'), 'estimate': i.get('epsEstimated')} for i in data[:5]]
    return results

now = datetime.now().strftime('%d.%m.%Y %H:%M')
print(f"=== Update {now} ===")

prices = fetch_prices(TICKERS)
print(f"Prices: {len(prices)}")

print("Fundamentals:")
funds = fetch_fundamentals(STOCK_TICKERS)
print(f"Got {len(funds)}")

print("Earnings:")
earn = fetch_earnings(STOCK_TICKERS)
print(f"Got {len(earn)}")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_block = (
    f"/* PRICES_INJECT */\n"
    f"const INJECTED_PRICES = {json.dumps(prices)};\n"
    f"const INJECTED_TIMESTAMP = '{now}';\n"
    f"const INJECTED_FUNDAMENTALS = {json.dumps(funds)};\n"
    f"const INJECTED_EARNINGS = {json.dumps(earn)};"
)

html = re.sub(
    r'/\* PRICES_INJECT \*/.*?const INJECTED_EARNINGS = \{.*?\};',
    new_block, html, flags=re.DOTALL
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Done: index.html updated")
