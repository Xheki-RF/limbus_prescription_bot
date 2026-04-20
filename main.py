import discord
from discord.ext import commands
from discord import Activity, ActivityType
import logging
from dotenv import load_dotenv
import os
import asyncio
from prescript import *
from datetime import datetime
import pytz
import pandas as pd


load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

active_prescripts = set()

MSK = pytz.timezone("Europe/Moscow")

bot = commands.Bot(command_prefix='!', intents=intents, handler=handler)


@bot.event
async def on_ready():
    global last_used
    await bot.change_presence(activity=Activity(type=ActivityType.listening, name="!prescript"), status=discord.Status.dnd)
    
    try:
        df = pd.read_csv("logs_info.csv")
        
        last_used = dict(zip(df["user_id"], df["date_logged"]))
    
    except Exception as e:
        print(f"Could not load logs_info.csv: {e}")
        last_used = {}

    print(f'Logged in as {bot.user}')


@bot.event
async def on_member_join(member):
    print(f'{member} has joined the server!')


@bot.command()
async def prescript(ctx):
    user_id = ctx.author.id

    now_msk = datetime.now(MSK)
    today = str(now_msk.date())

    # daily check to prevent multiple prescripts in one day
    if user_id in last_used and last_used[user_id] == today:
        warning_message = await ctx.send(f"{ctx.author.mention} You have already generated a prescript today!")

        await asyncio.sleep(2)

        await ctx.message.delete()
        await warning_message.delete()

        return

    # prevent multiple prescripts at the same time
    if user_id in active_prescripts:
        warning_message = await ctx.send(f"{ctx.author.mention} You already have a prescript generating!")
        
        time.sleep(2)
        await ctx.message.delete()
        await warning_message.delete()

        return

    active_prescripts.add(user_id)

    status_message = await ctx.send(f"{ctx.author.mention} Generating prescript...")

    try:
        text = await asyncio.to_thread(generate_prescript)

        last_used[user_id] = today

        df = pd.DataFrame(last_used.items(), columns=["user_id", "date_logged"])
        df.to_csv("logs_info.csv", index=False)

        await status_message.delete()

        await ctx.send(f"{ctx.author.mention} {text}")

    except Exception as e:
        await status_message.delete()
        await ctx.send(f"An error occurred: {e}")

    finally:
        active_prescripts.discard(user_id)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)