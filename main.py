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

    await ctx.send("Reminder Set!")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def clear(ctx, db):

    if db == "reminders":
        with open("reminders.json", "w") as f:
            json.dump({"mon": {}, "tue": {}, "wed": {}, "thu": {}, "fri": {}, "sat": {}, "sun": {}}, f)
        await ctx.send("Reminders Cleared!")
        return
    
    if db == "nicks":
        with open("nicks.json", "w") as f:
            json.dump({"mon": [], "tue": [], "wed": [], "thu": [], "fri": [], "sat": [], "sun": []}, f)
        await ctx.send("Nicks Cleared!")
        return
    
    await ctx.send("Unknown Database!")

@bot.command()
async def nick(ctx, day, nick):
    
    with open("nicks.json", "r") as f:
        data = json.load(f)
    
    data[day].append({"member": ctx.author.id, "guild": ctx.guild.id, "nick": nick})

    with open("nicks.json", "w") as f:
        json.dump(data, f)

    await ctx.send("Nick Set!")

@tasks.loop(seconds=60)
@commands.has_permissions(manage_channels=True)
async def loop():

    with open("reminders.json", "r") as f:
        data = json.load(f)

    reminders = data[days[datetime.today().weekday()]]
    time = datetime.now().strftime("%H:%M")
    if time in reminders:
        content = reminders[time]
        channel = bot.get_channel(int(content["channel"]))
        await channel.send(content["message"])

"""
@loop.error
async def loop_error(self, error, ctx):
    print("caught error")
    if isinstance(error, error.MissingPermissions):
        print("test")
"""

@bot.listen()
async def on_ready():
    
    with open("nicks.json", "r") as f:
        data = json.load(f)
    nicks = data[days[datetime.today().weekday()]]
    for triple in nicks:
        guild = bot.get_guild(triple["guild"])
        member = await guild.fetch_member(triple["member"])
        await member.edit(nick=triple["nick"])

    loop.start()

bot.run(os.getenv('TOKEN'))