import discord
from discord.ext import tasks, commands

import os
from dotenv import load_dotenv

import json

from datetime import datetime

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

@bot.command()
async def reminder(ctx, day, time, message, channel):
    
    with open("reminders.json", "r") as f:
        data = json.load(f)
    
    data[day][time] = {"message": message, "channel": channel[2:-1]}

    with open("reminders.json", "w") as f:
        json.dump(data, f)

    await ctx.send("Done!")

@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx):

    with open("reminders.json", "w") as f:
        json.dump({"mon": {}, "tue": {}, "wed": {}, "thu": {}, "fri": {}, "sat": {}, "sun": {}}, f)

    await ctx.send("Done!")

@tasks.loop(seconds=60)
@commands.has_permissions(administrator=True)
async def loop():

    with open("reminders.json", "r") as f:
        data = json.load(f)

    reminders = data[days[datetime.today().weekday()]]
    time = datetime.now().strftime("%H:%M")
    if time in reminders:
        content = reminders[time]
        await bot.get_channel(int(content["channel"])).send(content["message"])

@bot.listen()
async def on_ready():
    loop.start()

bot.run(os.getenv('TOKEN'))