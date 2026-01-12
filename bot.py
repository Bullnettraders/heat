import discord
import os
from discord.ext import commands, tasks
# NUR diese beiden Funktionen importieren:
from ticker_channels import update_ticker_channels, update_overall_trend_channel

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

TICKER_CHANNEL_IDS = [int(os.getenv(f"TICKER_CHANNEL_{i}")) for i in range(1, 11)]
OVERALL_TREND_CHANNEL = int(os.getenv("OVERALL_TREND_CHANNEL"))

@bot.event
async def on_ready():
    print(f"Bot ist online: {bot.user}")
    if not update_all.is_running():
        update_all.start()

@tasks.loop(minutes=3)
async def update_all():
    try:
        await update_ticker_channels(bot, TICKER_CHANNEL_IDS)
        await update_overall_trend_channel(bot, OVERALL_TREND_CHANNEL)
        print("Erfolgreich aktualisiert (schnelle Methode).")
    except Exception as e:
        print(f"Fehler im Loop: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))
