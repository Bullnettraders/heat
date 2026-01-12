import yfinance as yf
import pandas as pd

# Deine Top 10
TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST"]

def get_price_changes_fast(ticker_list):
    """Holt alle Kurse gleichzeitig - viel schneller als .info"""
    # Wir laden die Daten der letzten 2 Minuten für alle Ticker gleichzeitig
    data = yf.download(ticker_list, period="1d", interval="1m", group_by='ticker', progress=False)
    
    changes = {}
    for ticker in ticker_list:
        try:
            # Schnelle Berechnung der Kursänderung
            ticker_data = data[ticker]
            current = ticker_data['Close'].iloc[-1]
            prev = ticker_data['Close'].iloc[0]
            change = ((current - prev) / prev) * 100
            changes[ticker] = round(change, 2)
        except:
            continue
    return changes

def format_ticker(ticker, change):
    if change > 0.3: symbol = "🟢"
    elif change < -0.3: symbol = "🔴"
    else: symbol = "🟡"
    return f"{symbol} {ticker} {change:+.2f}%"

async def update_ticker_channels(bot, channel_ids):
    # Alle 10 Ticker in 1 Sekunde abrufen
    changes = get_price_changes_fast(TICKERS)
    for i, ticker in enumerate(TICKERS):
        if i >= len(channel_ids): break
        channel = bot.get_channel(channel_ids[i])
        if channel and ticker in changes:
            new_name = format_ticker(ticker, changes[ticker])
            # Nur bearbeiten, wenn der Name sich wirklich geändert hat (spart API-Limit)
            if channel.name != new_name:
                await channel.edit(name=new_name)

async def update_overall_trend_channel(bot, channel_id):
    # Top 100 Ticker für den Gesamt-Trend holen
    url = "https://en.wikipedia.org/wiki/NASDAQ-100"
    tables = pd.read_html(url)
    all_tickers = tables[4]['Ticker'].tolist()[:100]
    all_tickers = [t.replace(".", "-") for t in all_tickers]
    
    # Auch hier: Alles im Bulk-Download
    changes = get_price_changes_fast(all_tickers)
    if not changes: return
    
    avg = sum(changes.values()) / len(changes)
    
    if avg > 0.3: symbol, label = "🟢", "steigt"
    elif avg < -0.3: symbol, label = "🔴", "fällt"
    else: symbol, label = "🟡", "neutral"

    name = f"{symbol} NAS-100: {avg:+.2f}%"
    channel = bot.get_channel(channel_id)
    if channel and channel.name != name:
        await channel.edit(name=name)
