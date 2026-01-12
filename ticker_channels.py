import yfinance as yf

# Deine TOP 10
TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST"]

def get_price_changes_fast():
    # Wir laden alle 10 Ticker gleichzeitig (Bulk)
    # period="1d" reicht aus, um die Tagesänderung zu bekommen
    data = yf.download(TICKERS, period="1d", interval="1m", group_by='ticker', progress=False)
    
    changes = {}
    for ticker in TICKERS:
        try:
            # Wir holen den letzten und den vorletzten Schlusskurs für die Berechnung
            ticker_data = data[ticker]
            current_price = ticker_data['Close'].iloc[-1]
            prev_close = ticker_data['Close'].iloc[0]
            
            # Prozentuale Änderung berechnen
            change_pct = ((current_price - prev_close) / prev_close) * 100
            changes[ticker] = round(change_pct, 2)
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
    # Hier nutzen wir jetzt die schnelle Abfrage
    changes = get_price_changes_fast()
    for i, ticker in enumerate(TICKERS):
        if i >= len(channel_ids):
            break
        channel = bot.get_channel(channel_ids[i])
        if channel and ticker in changes:
            name = format_ticker(ticker, changes[ticker])
            # Verhindert unnötige API-Calls, wenn der Name schon gleich ist
            if channel.name != name:
                await channel.edit(name=name)
