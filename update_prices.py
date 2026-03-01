#!/usr/bin/env python3
import json, re
from datetime import datetime
import yfinance as yf

TICKERS = [
    "AMZN","BAS.DE","BAYN.DE","BMW.DE","HLAG.DE","HEIG.DE",
    "KHC","LHA.DE","NVO","PFE","RWE.DE","NFLX","SPOT","CMCSA",
    "IWDA.AS","GDX","XMEA.DE","SUOE.DE","QDVE.DE","EIMI.DE"
]

STOCK_TICKERS = [
    "AMZN","BAS.DE","BAYN.DE","BMW.DE","HLAG.DE","HEIG.DE",
    "KHC","LHA.DE","NVO","PFE","RWE.DE","NFLX","SPOT","CMCSA"
]

def fetch_prices(tickers):
    results = {}
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.fast_info
            price = info.last_price or 0
            prev  = info.previous_close or price
            change = ((price - prev) / prev * 100) if prev else 0
            currency = getattr(info, 'currency', '')
            results[ticker] = {
                'price': round(price, 4),
                'change': round(change, 4),
                'currency': currency,
            }
            print(f"  {ticker}: {price}")
        except Exception as e:
            print(f"  {ticker} Error: {e}")
    return results

def fetch_fundamentals(tickers):
    results = {}
    for ticker in tickers:
        print(f"  {ticker}")
        try:
            t = yf.Ticker(ticker)
            info = t.info
            entry = {}
            entry['pe']        = info.get('trailingPE')
            entry['marketCap'] = info.get('marketCap')
            entry['revenue']   = info.get('totalRevenue')
            entry['netIncome'] = info.get('netIncomeToCommon')

            # Analyst rating
            rec = info.get('recommendationKey', '')
            mapping = {
                'strong_buy': 'Strong Buy',
                'buy': 'Buy',
                'hold': 'Halten',
                'sell': 'Sell',
                'strong_sell': 'Strong Sell'
            }
            entry['rating'] = mapping.get(rec, '')

            results[ticker] = entry
        except Exception as e:
            print(f"  {ticker} Error: {e}")
    return results

def fetch_earnings(tickers):
    results = {}
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            cal = t.earnings_dates
            if cal is not None and not cal.empty:
                entries = []
                for date, row in cal.head(5).iterrows():
                    entries.append({
                        'date': str(date.date()),
                        'label': str(date.date()),
                        'actual': row.get('Reported EPS'),
                        'estimate': row.get('EPS Estimate'),
                    })
                results[ticker] = entries
        except Exception as e:
            print(f"  {ticker} Error: {e}")
    return results

now = datetime.now().strftime('%d.%m.%Y %H:%M')
print(f"=== Update {now} ===")

print("Prices:")
prices = fetch_prices(TICKERS)
print(f"Got {len(prices)}")

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
