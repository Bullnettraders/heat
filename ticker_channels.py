import yfinance as yf
import pandas as pd
import os

TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST"]

def get_price_changes():
    changes = {}
    for ticker in TICKERS:
        try:
            info = yf.Ticker(ticker).info
            change = info.get("regularMarketChangePercent")
            if change is not None:
                changes[ticker] = round(change, 2)
        except:
            continue
    return changes

def format_ticker(ticker, change):
    if change > 0.3:
        symbol = "🟢"
    elif change < -0.3:
        symbol = "🔴"
    else:
        symbol = "🟡"
    return f"{symbol} {ticker} {change:+.2f}%"

async def update_ticker_channels(bot, channel_ids):
    changes = get_price_changes()
    for i, ticker in enumerate(TICKERS):
        if i >= len(channel_ids):
            break
        channel = bot.get_channel(channel_ids[i])
        if channel and ticker in changes:
            name = format_ticker(ticker, changes[ticker])
            await channel.edit(name=name)

def get_nasdaq100_tickers():
    url = "https://en.wikipedia.org/wiki/NASDAQ-100"
    tables = pd.read_html(url)
    tickers = tables[4]['Ticker'].tolist()
    tickers = [t.replace(".", "-") for t in tickers]
    return tickers

async def update_overall_trend_channel(bot, channel_id):
    tickers = get_nasdaq100_tickers()
    changes = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            change = info.get("regularMarketChangePercent")
            if change is not None:
                changes.append(change)
        except:
            continue

    if not changes:
        return

    avg = sum(changes) / len(changes)

    if avg > 0.3:
        symbol = "🟢"
        label = "steigt"
    elif avg < -0.3:
        symbol = "🔴"
        label = "fällt"
    else:
        symbol = "🟡"
        label = "neutral"

    name = f"{symbol} NASDAQ-100 {label}: {avg:+.2f}%"
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.edit(name=name)
