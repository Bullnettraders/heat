import yfinance as yf
import pandas as pd
from datetime import datetime

# ═══ BULLNET_SPEICHER ═══
# Die Wikipedia-Liste wurde alle drei Minuten neu geladen und geparst --
# 480 Abrufe am Tag fuer eine Liste, die sich ein paarmal im Jahr aendert.
# Dazu blieben die pandas-Tabellen im Speicher liegen.
_liste = None
_liste_stand = None
_trend_wert = None
_trend_stand = None

TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST"]

def get_price_changes_fast(ticker_list):
    # Zwei Tage reichen fuer den Vergleich zum Vortag.
    data = yf.download(ticker_list, period="2d", interval="1d", progress=False)

    changes = {}
    for ticker in ticker_list:
        try:
            current_price = data['Close'][ticker].iloc[-1]
            prev_close = data['Close'][ticker].iloc[-2]
            change_pct = ((current_price - prev_close) / prev_close) * 100
            changes[ticker] = round(change_pct, 2)
        except Exception as e:
            continue
    del data
    return changes


def _nasdaq100_liste():
    # Einmal am Tag genuegt.
    global _liste, _liste_stand
    jetzt = datetime.now()
    if _liste and _liste_stand and (jetzt - _liste_stand).total_seconds() < 86400:
        return _liste
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/NASDAQ-100")
        _liste = [t.replace(".", "-") for t in tables[4]['Ticker'].tolist()[:100]]
        _liste_stand = jetzt
        del tables
    except Exception as e:
        print(f"NASDAQ-100 Liste: {e}")
    return _liste or []

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
    # Nur alle 30 Minuten wirklich rechnen -- fuer eine Kanalueberschrift
    # reicht das voellig, statt alle drei Minuten 100 Aktien zu laden.
    global _trend_wert, _trend_stand
    jetzt = datetime.now()
    if _trend_stand and (jetzt - _trend_stand).total_seconds() < 1800:
        avg = _trend_wert
        if avg is None: return
    else:
        all_tickers = _nasdaq100_liste()
        if not all_tickers: return
        changes = get_price_changes_fast(all_tickers)
        if not changes: return
        avg = sum(changes.values()) / len(changes)
        _trend_wert = avg
        _trend_stand = jetzt
    
    # Dynamische Symbole für den Trend
    if avg > 0.3: symbol = "🟢"
    elif avg < -0.3: symbol = "🔴"
    else: symbol = "🟡"

    name = f"{symbol} NASDAQ-100: {avg:+.2f}%"
    channel = bot.get_channel(channel_id)
    if channel and channel.name != name:
        await channel.edit(name=name)
