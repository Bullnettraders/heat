import yfinance as yf
import pandas as pd

TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST"]

def get_price_changes_fast(ticker_list):
    # Wir laden die Daten für 5 Tage, um sicherzugehen, dass wir den letzten Schlusskurs haben
    # (Wichtig für Wochenenden oder Feiertage)
    data = yf.download(ticker_list, period="5d", interval="1d", progress=False)
    
    changes = {}
    for ticker in ticker_list:
        try:
            # .iloc[-1] ist der heutige (aktuelle) Kurs
            # .iloc[-2] ist der Schlusskurs vom letzten Handelstag (Gestern/Freitag)
            current_price = data['Close'][ticker].iloc[-1]
            prev_close = data['Close'][ticker].iloc[-2]
            
            # Die echte tägliche Änderung berechnen
            change_pct = ((current_price - prev_close) / prev_close) * 100
            changes[ticker] = round(change_pct, 2)
        except Exception as e:
            continue
    return changes

def format_ticker(ticker, change):
    # Schwellenwert: 0.3% für eine klare Farbtrennung
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
            new_name = format_ticker(ticker, changes[ticker])
            if channel.name != new_name:
                await channel.edit(name=new_name)

async def update_overall_trend_channel(bot, channel_id):
    # NASDAQ-100 Liste holen
    url = "https://en.wikipedia.org/wiki/NASDAQ-100"
    tables = pd.read_html(url)
    all_tickers = tables[4]['Ticker'].tolist()[:100]
    all_tickers = [t.replace(".", "-") for t in all_tickers]
    
    # Trend basierend auf dem Vergleich zum Vortag
    changes = get_price_changes_fast(all_tickers)
    if not changes: return
    
    avg = sum(changes.values()) / len(changes)
    
    # Dynamische Symbole für den Trend
    if avg > 0.3: symbol = "🟢"
    elif avg < -0.3: symbol = "🔴"
    else: symbol = "🟡"

    name = f"{symbol} NASDAQ-100: {avg:+.2f}%"
    channel = bot.get_channel(channel_id)
    if channel and channel.name != name:
        await channel.edit(name=name)
