import discord
import os
from discord.ext import commands, tasks
# Nur die Funktionen importieren, die wirklich in ticker_channels.py existieren
from ticker_channels import update_ticker_channels, update_overall_trend_channel

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# IDs sicher aus den Railway-Umgebungsvariablen laden
TICKER_CHANNEL_IDS = [
    int(os.getenv(f"TICKER_CHANNEL_{i}")) for i in range(1, 11)
]
OVERALL_TREND_CHANNEL = int(os.getenv("OVERALL_TREND_CHANNEL"))

@bot.event
async def on_ready():
    print(f"🚀 Bot erfolgreich gestartet: {bot.user}")
    # Startet die Schleife nur, wenn sie nicht schon läuft
    if not update_all.is_running():
        update_all.start()

@tasks.loop(minutes=3)
async def update_all():
    try:
        # 1. Die 10 Ticker-Kanäle aktualisieren
        await update_ticker_channels(bot, TICKER_CHANNEL_IDS)
        
        # 2. Den NASDAQ-Trend-Kanal aktualisieren
        await update_overall_trend_channel(bot, OVERALL_TREND_CHANNEL)
        
        print("✅ Update erfolgreich (Schnelle Bulk-Methode)")
    except Exception as e:
        print(f"❌ Fehler beim Update: {e}")

# Railway Start-Befehl
bot.run(os.getenv("DISCORD_TOKEN"))
