import discord
from discord.ext import commands

from karen.evaluate import evaluate
from karen.getCombo import *

import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN") # save your bot token as an environment variable or paste it here
print(BOT_TOKEN)

intents = discord.Intents.default()
intents.guild_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def eval(ctx, *arr):
    inputString = "".join(str(x) for x in arr)
    output = evaluate(inputString)
    try:
        await ctx.send(output)
    except Exception as e:
        print(e)

@bot.command()
async def evaln(ctx, *arr):
    inputString = "".join(str(x) for x in arr)
    output = evaluate(inputString, printWarnings=False)
    try:
        await ctx.send(output)
    except Exception as e:
        print(e)

@bot.command()
async def combo(ctx, *arr):
    inputString = "".join(str(x) for x in arr)
    output = getCombo(inputString)
    try:
        await ctx.send(output)
    except Exception as e:
        print(e)

@bot.command()
async def combos(ctx, *arr):
    output = listCombos()
    try:
        await ctx.send(output)
    except Exception as e:
        print(e)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        await bot.tree.sync()
        print("synced successfully")
    except Exception as e:
        print(e)
    

bot.run(BOT_TOKEN)