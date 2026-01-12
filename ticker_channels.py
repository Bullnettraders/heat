import yfinance as yf
import pandas as pd

TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST"]

def get_price_changes_fast(ticker_list):
    # Bulk-Abfrage für maximale Geschwindigkeit
    data = yf.download(ticker_list, period="1d", interval="1m", group_by='ticker', progress=False)
    changes = {}
    for ticker in ticker_list:
        try:
            ticker_data = data[ticker]
            current_price = ticker_data['Close'].iloc[-1]
            prev_close = ticker_data['Close'].iloc[0]
            change_pct = ((current_price - prev_close) / prev_close) * 100
            changes[ticker] = round(change_pct, 2)
        except:
            continue
    return changes

def format_ticker(ticker, change):
    if change > 0.3: symbol = "🟢"
    elif change < -0.3: symbol = "🔴"
    else: symbol = "🟡"
    return f"{symbol} {ticker} {change:+.2f}%"

async def update_ticker_channels(bot, channel_ids):
    changes = get_price_changes_fast(TICKERS)
    for i, ticker in enumerate(TICKERS):
        if i >= len(channel_ids): break
        channel = bot.get_channel(channel_ids[i])
        if channel and ticker in changes:
            name = format_ticker(ticker, changes[ticker])
            if channel.name != name:
                await channel.edit(name=name)

async def update_overall_trend_channel(bot, channel_id):
    # NASDAQ-100 Trend berechnen
    url = "https://en.wikipedia.org/wiki/NASDAQ-100"
    tables = pd.read_html(url)
    all_tickers = tables[4]['Ticker'].tolist()[:100] # Top 100
    all_tickers = [t.replace(".", "-") for t in all_tickers]
    
    changes = get_price_changes_fast(all_tickers)
    if not changes: return
    
    avg = sum(changes.values()) / len(changes)
    
    if avg > 0.3: symbol, label = "🟢", "steigt"
    elif avg < -0.3: symbol, label = "🔴", "fällt"
    else: symbol, label = "🟡", "neutral"

    name = f"{symbol} NASDAQ-100: {avg:+.2f}%"
    channel = bot.get_channel(channel_id)
    if channel and channel.name != name:
        await channel.edit(name=name)
