import discord
import asyncio
import os
from discord.ext import commands, tasks
# Hier importieren wir deine Funktionen aus der anderen Datei
from ticker_channels import update_ticker_channels, update_overall_trend_channel, generate_top10_heatmap

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Deine IDs aus der .env Datei
TICKER_CHANNEL_IDS = [
    int(os.getenv(f"TICKER_CHANNEL_{i}")) for i in range(1, 11)
]
OVERALL_TREND_CHANNEL = int(os.getenv("OVERALL_TREND_CHANNEL"))

@bot.event
async def on_ready():
    print(f"Bot ist online: {bot.user}")
    update_all.start() # Startet die Schleife, wenn der Bot bereit ist

# --- HIER KOMMT DER NEUE BLOCK HIN ---
@tasks.loop(minutes=3)
async def update_all():
    try:
        # 1. Aktualisiert die Namen der 10 einzelnen Kanäle
        await update_ticker_channels(bot, TICKER_CHANNEL_IDS)
        
        # 2. Aktualisiert den Trend-Kanal Namen
        await update_overall_trend_channel(bot, OVERALL_TREND_CHANNEL)

        # 3. Erstellt die visuelle Heatmap und postet sie in den Trend-Kanal
        channel = bot.get_channel(OVERALL_TREND_CHANNEL)
        if channel:
            # Die Funktion erstellt das Bild und gibt den Dateipfad zurück
            path = generate_top10_heatmap()
            
            if path:
                # Löscht alte Bot-Nachrichten, damit der Kanal nicht vollgespammt wird
                await channel.purge(limit=5, check=lambda m: m.author == bot.user)
                
                # Sendet das neue Bild hoch
                file = discord.File(path, filename="heatmap.png")
                await channel.send("📊 **Top 10 Markt-Übersicht (Heatmap)**", file=file)
                
    except Exception as e:
        print(f"[Fehler beim Update] {e}")
# -------------------------------------

bot.run(os.getenv("DISCORD_TOKEN"))
