import discord
from discord.ext import commands
from discord import Activity, ActivityType
import logging
from dotenv import load_dotenv
import os
import asyncio
from prescript import *


load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

active_prescripts = set()

bot = commands.Bot(command_prefix='!', intents=intents, handler=handler)


@bot.event
async def on_ready():
    await bot.change_presence(activity=Activity(type=ActivityType.listening, name="!prescript"), status=discord.Status.dnd)
    print(f'Logged in as {bot.user}')


@bot.event
async def on_member_join(member):
    print(f'{member} has joined the server!')


@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def prescript(ctx):
    user_id = ctx.author.id

    if user_id in active_prescripts:
        await ctx.message.delete()

        warning_message = await ctx.send(f"{ctx.author.mention} You already have a prescript generating!")
        time.sleep(2)
        await warning_message.delete()

        return

    active_prescripts.add(user_id)

    try:
        status_message = await ctx.send(f"{ctx.author.mention} Generating prescript...")
        
        text = await asyncio.to_thread(generate_prescript)

        await status_message.delete()

        await ctx.send(f"{ctx.author.mention} {text}")

    except Exception as e:
        await status_message.delete()
        await ctx.send(f"An error occurred: {e}")

    finally:
        active_prescripts.discard(user_id)


@prescript.error
async def prescript_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        remaining = int(error.retry_after)

        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        await ctx.send(f"{ctx.author.mention} you can use this again in {hours}h {minutes}m")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)