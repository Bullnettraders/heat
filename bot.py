import discord, asyncio, os
from discord.ext import commands, tasks
from heatmap import generate_heatmap

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

TICKERS = os.getenv("STOCKS", "AAPL,MSFT,NVDA,GOOG,TSLA").split(",")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")
    post_heatmap.start()

@tasks.loop(minutes=3)
async def post_heatmap():
    generate_heatmap(TICKERS)
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(file=discord.File("heatmap.png"))

bot.run(os.getenv("DISCORD_TOKEN"))
