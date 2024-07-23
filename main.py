import discord
import os
from discord.ext import commands, tasks
import sys
import ast
import traceback
import datetime
from threading import Thread
import webserver
from utility import jsonhandler
from utility import blackjack
from utility import ships
from utility import upgrades
from utility.paginator import Pag
from utility import srads
from utility import relations
from utility import offduty
from utility import ranks
from utility import warns
from utility import commandingOfficers
from utility import eventhandler
from utility import pointlog
from utility import points
from copy import deepcopy
from textwrap import wrap
import requests
import json
import random
import re
import asyncio
from gpiozero import CPUTemperature
import psutil
import plotly.express as px
import pandas as pd
import openai
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-d", "--development", help="Runs outside raspberry pi")

args = parser.parse_args()

if not args.development:
    os.chdir("/home/bongo/Downloads/UFPAnnouncements")

def getConfig(key):
    with open("config.json", "r") as f:
        data = json.load(f)

    return data[key]

client = openai.Client(
    api_key=getConfig("openai")
)

from PIL import ImageDraw, Image, ImageFont

colors = {
    "Orange": "#FD9B00",
    "Purple": "#854287",
    "Bright Purple": "#CB99CC",
    "Blonde": "#E7BD63"
}

bot = discord.Bot(intents=discord.Intents.all())
latinumTypes = ["Bars", "Strips", "Slips"]
latinumTypesLower = ["bars", "strips", "slips"]

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d||))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400,"":1}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)

exchanges = {
    "bars": {
        "strips": 20,
        "slips": 2000
    },
    "strips": {
        "bars": 1/20,
        "slips": 100
    },
    "slips": {
        "bars": 1/2000,
        "strips": 1/100
    }
}

async def getLatinumTypes(ctx):
    return [latinumType for latinumType in latinumTypes if latinumType.lower().startswith(ctx.value.lower())]

async def getAllies(ctx):
    return [ally for ally in relations.getAllies() if ally.startswith(ctx.value)]

async def getFriendlies(ctx):
    return [friendly for friendly in relations.getFriendlies() if friendly.startswith(ctx.value)]

async def getEnemies(ctx):
    return [enemy for enemy in relations.getEnemies().keys() if enemy.startswith(ctx.value)]

async def getTypes(ctx):
    return [label for label in ["Terrorist Organization"] if label.startswith(ctx.value)]

async def getRank(member):
    UFP = await bot.fetch_guild(878364507385233480)

    captain = discord.utils.get(UFP.roles, id=878367800937304146)
    RALH = discord.utils.get(UFP.roles, id=940456287496470578)
    RAUH = discord.utils.get(UFP.roles, id=1022239558093512825)
    VA = discord.utils.get(UFP.roles, id=940456210799411220)
    ADM = discord.utils.get(UFP.roles, id=878367592706887761)
    FADM = discord.utils.get(UFP.roles, id=940455959858413658)

    if captain in member.roles:
        return "Captain"
    if RALH in member.roles:
        return "Admiral"
    if RAUH in member.roles:
        return "Admiral"
    if VA in member.roles:
        return "Admiral"
    if ADM in member.roles:
        return "Admiral"
    if FADM in member.roles:
        return "Admiral"

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

bot.mentioned = False

def wrapString(string):
    linebreak = string.split("\n")
    buffer = ""
    final = []

    for line in linebreak:
        if len(buffer + "\n" + line) > 2000:
            final.append(buffer)
            buffer = line
        else:
            buffer += "\n{}".format(line)

    final.append(buffer)

    for item in final:
        print(len(item))

    return final

def CreateEventEmbed(Guild: discord.Guild, EventType: str, EventTimestamp: int, EventHost: discord.Member, EventNotes: str, EventDuration: int, EventID: str) -> discord.Embed:
    Colors = {
        "Training": 0x0452cf,
        "Testing": 0x04cf66,
        "Patrol": 0xf5d502,
        "Workshop": 0x6f02f5,
        "Battle": 0xf53b02
    }

    StarterEmbed = discord.Embed(
        timestamp=datetime.datetime.now(),
        color=Colors[EventType]
    )
    StarterEmbed.add_field(name="Time", value="**In UTC**: {}\n**Relative**: <t:{}:R>".format(datetime.datetime.utcfromtimestamp(EventTimestamp), EventTimestamp), inline=False)
    StarterEmbed.add_field(name="Event Duration", value="{} Minutes".format(EventDuration), inline=False)
    StarterEmbed.add_field(name="Host", value=str(EventHost), inline=False)
    StarterEmbed.add_field(name="Notes", value=EventNotes, inline=False)
    StarterEmbed.add_field(name="Event Type", value=EventType, inline=False)
    StarterEmbed.add_field(name="Event ID", value=EventID, inline=False)
    StarterEmbed.set_footer(text="Secure Event- Do not share outside of UFP")
    StarterEmbed.set_author(name="United Federation of Planets", icon_url=Guild.icon.url)

    return StarterEmbed

class EventButton(discord.ui.Button):
    def __init__(self, Label: str, PointlogID: str):
        super().__init__(label=Label, custom_id="{} | {}".format(Label, PointlogID), style=discord.ButtonStyle.gray)

@bot.command(name="create-event", description="Create a classified event for Commissioned Personnel (TIME MUST BE IN UTC)", guild_ids=[878364507385233480])
@discord.commands.option("eventtype", choices=["Training", "Patrol", "Workshop", "Testing", "Battle"])
@discord.commands.option("eventminute", choices=[0, 15, 30, 45])
@discord.commands.option("eventduration", choices=[15, 30, 45, 60, 75, 90, 105, 120])
async def createEvent(ctx: discord.ApplicationContext, eventtype, eventnotes: str, eventduration: int, eventday: int=None, eventmonth: int=None, eventyear: int=None, eventhour: int=None, eventminute: int=None):
    await ctx.defer()

    msg = await ctx.respond("Scheduling Event...")

    nowUTCTime = datetime.datetime.now()
    EventTimestamp = datetime.datetime(
        year=eventyear or nowUTCTime.year, 
        month=eventmonth or nowUTCTime.month, 
        day=eventday or nowUTCTime.day,
        hour=eventhour or nowUTCTime.hour,
        minute=eventminute or 0
    )

    EventTimestamp -= datetime.timedelta(hours=5)

    if EventTimestamp < nowUTCTime and EventTimestamp + datetime.timedelta(hours=12) >= nowUTCTime:
        EventTimestamp += datetime.timedelta(hours=12)
    if EventTimestamp < nowUTCTime and EventTimestamp + datetime.timedelta(hours=12) < nowUTCTime:
        return await ctx.respond("Event time has already passed")

    EventID = eventhandler.CreateEvent(eventtype, int(EventTimestamp.timestamp()), ctx.author, eventnotes, eventduration)

    await msg.edit("Creating Embed...")

    events = await ctx.guild.fetch_channel(1263544155691286639)

    Embed = CreateEventEmbed(ctx.guild, eventtype, int(EventTimestamp.timestamp()), ctx.author, eventnotes, eventduration, EventID)

    await msg.edit("Sending Event Embed Into <#{}>...".format(events.id))

    View = discord.ui.View()
    View.add_item(EventButton("View Event", EventID))

    await events.send("**A new event has been scheduled.**", view=View)

    await msg.edit("Successfully scheduled the event.")

@bot.command(name="get-event", description="Retrive an event created", guild_ids=[878364507385233480])
async def GetEvent(ctx: discord.ApplicationContext, eventid: str):
    Event = eventhandler.GetEvent(eventid)
    if not Event:
        return await ctx.respond("Event not found.")

    await ctx.respond(embed=CreateEventEmbed(ctx.guild, Event["EventType"], Event["EventTimestamp"], ctx.guild.get_member(Event["EventHost"]), Event["EventNotes"], Event["EventDuration"], eventid))

@bot.command(name="edit-event", description="Retrive an event created", guild_ids=[878364507385233480])
async def GetEvent(ctx: discord.ApplicationContext, eventid: str, eventnotes: str=None, eventduration: int=None, eventday: int=None, eventmonth: int=None, eventyear: int=None, eventhour: int=None, eventminute: int=None):
    Event = eventhandler.GetEvent(eventid)
    if not Event:
        return await ctx.respond("Event not found.")
    
    View = discord.ui.View()
    View.add_item(EventButton("View Event", eventid))

    nowUTCTime = datetime.datetime.now()
    TimeFromTimestamp = datetime.datetime.fromtimestamp(Event["EventTimestamp"])
    
    EventTimestamp = datetime.datetime(
        year=eventyear or TimeFromTimestamp.year, 
        month=eventmonth or TimeFromTimestamp.month, 
        day=eventday or TimeFromTimestamp.day,
        hour=eventhour or TimeFromTimestamp.hour,
        minute=eventminute or TimeFromTimestamp.minute
    )

    if eventhour:
        EventTimestamp -= datetime.timedelta(hours=5)

    if EventTimestamp < nowUTCTime and EventTimestamp + datetime.timedelta(hours=12) >= nowUTCTime:
        EventTimestamp += datetime.timedelta(hours=12)
    if EventTimestamp < nowUTCTime and EventTimestamp + datetime.timedelta(hours=12) < nowUTCTime:
        return await ctx.respond("Event time has already passed")
    
    Event = eventhandler.EditEvent(eventid, EventTimestamp=int(EventTimestamp.timestamp()), EventNotes=eventnotes, EventDuration=eventduration)

    events = await ctx.guild.fetch_channel(1263544155691286639)
    await events.send("**An event has been updated**", view=View)

    await ctx.respond("Event updated.")

@bot.command(name="delete-event", description="Delete an event created", guild_ids=[878364507385233480])
async def DeleteEvent(ctx: discord.ApplicationContext, eventid: str):
    Event = eventhandler.GetEvent(eventid)
    if not Event:
        return await ctx.respond("Event not found.")
    
    eventhandler.DeleteEvent(eventid)

    await ctx.respond("Deleted")

@tasks.loop(minutes=1)
async def EventReminder():
    UFP = bot.get_guild(878364507385233480)
    EventChannel = UFP.get_channel(1263544155691286639)

    Events = eventhandler.ReadJson()
    TimestampNow = datetime.datetime.now().timestamp()

    for EventID, EventData in Events.items():
        if EventData["EventTimestamp"] - 3600 > TimestampNow:
            continue

        if EventData["EventTimestamp"] + (EventData["EventDuration"] * 60) <= TimestampNow:
            eventhandler.DeleteEvent(EventID)
            continue

        if not EventData["Reminded"]:
            EventData["Reminded"] = True

            EventEmbed = CreateEventEmbed(UFP, EventData["EventType"], EventData["EventTimestamp"], UFP.get_member(EventData["EventHost"]), EventData["EventNotes"], EventData["EventDuration"], EventID)

            await EventChannel.send("<@&954234917846388826> **This event starts in less than an hour.**", embed=EventEmbed)

            eventhandler.EditEvent(EventID, EventData)

        if EventData["EventTimestamp"] < TimestampNow and not EventData["Announced"]:
            EventData["Announced"] = True

            EventEmbed = CreateEventEmbed(UFP, EventData["EventType"], EventData["EventTimestamp"], UFP.get_member(EventData["EventHost"]), EventData["EventNotes"], EventData["EventDuration"], EventID)

            await EventChannel.send("<@&954234917846388826> **This event has started.**", embed=EventEmbed)

            eventhandler.EditEvent(EventID, EventData)

@tasks.loop(minutes=10)
async def PointChecker():
    UFP = bot.get_guild(878364507385233480)
    RankUpdate = UFP.get_channel(1264001160172539905)

    Points = points.ReadJson()

    async for Member in UFP.fetch_members(limit=1000):
        UserData = points.GetUser(Member.id)
    
        if UserData["Ranklocked"]:
            continue

        if UserData["WaitingForRankChange"]:
            continue
    
        if not ranks.getRank(Member):
            continue

        Rank = ranks.getRank(Member).id
        RankAbove = ranks.GetRankAbove(Member)

        PointRankAbove = ranks.requirements[str(RankAbove)]
        PointRankBelow = ranks.requirements[str(Rank)]

        if PointRankAbove and UserData["Points"] >= PointRankAbove:
            view = discord.ui.View()
            view.add_item(points.PointButton("Promote", str(Member.id)))
            view.add_item(points.PointButton("Minimum", str(Member.id)))

            Embed = discord.Embed(
                color=0x0452cf
            )
            Embed.set_author(name="United Federation of Planets", icon_url=UFP.icon.url)

            Embed.add_field(name="Member", value=str(Member), inline=False)
            Embed.add_field(name="Current Points", value=UserData["Points"], inline=False)
            Embed.add_field(name="Action", value="Promotion to <@&{}>".format(ranks.GetMinimumRank(UserData["Points"])), inline=False)
        elif PointRankBelow and UserData["Points"] < PointRankBelow:
            view = discord.ui.View()
            view.add_item(points.PointButton("Demote", str(Member.id)))
            view.add_item(points.PointButton("Minimum", str(Member.id)))

            Embed = discord.Embed(
                color=0x0452cf
            )
            Embed.set_author(name="United Federation of Planets", icon_url=UFP.icon.url)

            Embed.add_field(name="Member", value=str(Member), inline=False)
            Embed.add_field(name="Current Points", value=UserData["Points"], inline=False)
            Embed.add_field(name="Action", value="Demotion to <@&{}>".format(str(ranks.GetMinimumRank(UserData["Points"]))), inline=False)
        else:
            continue

        await RankUpdate.send(embed=Embed, view=view)

        UserData["WaitingForRankChange"] = True
        points.WriteKey(str(Member.id), UserData)


@bot.command(name="my-points", description="Find your points", guild_ids=[878364507385233480])
async def MyPoints(ctx: discord.ApplicationContext):
    Logs = pointlog.ReadJson()

    Pending = 0

    for LogID, Log in deepcopy(Logs).items():
        for Point, Users in Log["Log"].items():
            Point = int(Point)

            for User in Users:
                if User == ctx.author.id:
                    Pending += Point

    UserData = points.GetUser(ctx.author.id)

    Embed = discord.Embed(
        color=0x0452cf
    )
    Embed.set_author(name="United Federation of Planets", icon_url=ctx.guild.icon.url)
    Embed.add_field(name="Points", value="{} Points{}{}".format(UserData["Points"], f" ({Pending} Pending)" if Pending else "", "\n    Ranklocked" if UserData["Ranklocked"] else ""))

    await ctx.respond(embed=Embed)

@bot.command(name="get-points", description="Find someone else's points", guild_ids=[878364507385233480])
async def GetPoints(ctx: discord.ApplicationContext, member: discord.Member):
    Logs = pointlog.ReadJson()

    Pending = 0

    for LogID, Log in deepcopy(Logs).items():
        for Point, Users in Log["Log"].items():
            Point = int(Point)

            for User in Users:
                if User == member.id:
                    Pending += Point

    UserData = points.GetUser(member.id)

    Embed = discord.Embed(
        color=0x0452cf
    )
    Embed.set_author(name="United Federation of Planets", icon_url=ctx.guild.icon.url)
    Embed.add_field(name="Points", value="{} Points{}{}".format(UserData["Points"], f" ({Pending} Pending)" if Pending else "", "\n    Ranklocked" if UserData["Ranklocked"] else ""))

    await ctx.respond(embed=Embed)

@bot.command(name="my-logs", description="View the IDs of the logs that you've sent in", guild_ids=[878364507385233480])
async def ViewMyLogs(ctx: discord.ApplicationContext):
    Logs = pointlog.ReadJson()
    OwnedLogs = []

    Pending = 0

    for LogID, Log in deepcopy(Logs).items():
        if Log["Logger"] == ctx.author.id:
            OwnedLogs.append("`" + LogID + "`")

    Embed = discord.Embed(
        description="{}".format("\n".join(OwnedLogs)),
        color=0x0452cf
    )
    Embed.set_author(name="United Federation of Planets", icon_url=ctx.guild.icon.url)

    await ctx.respond(embed=Embed)

@bot.command(name="all-logs", description="View the IDs of the logs that are pending", guild_ids=[878364507385233480])
async def ViewPendingLogs(ctx: discord.ApplicationContext):
    Logs = pointlog.ReadJson()
    FormattedLogs = []

    for LogID, Log in deepcopy(Logs).items():
        FormattedLogs.append("`{}` - <@{}>".format(LogID, Log["Logger"]))

    Embed = discord.Embed(
        description="{}".format("\n".join(FormattedLogs)),
        color=0x0452cf
    )
    Embed.set_author(name="United Federation of Planets", icon_url=ctx.guild.icon.url)

    await ctx.respond(embed=Embed)

@bot.command(name="view-log", description="View a pointlog", guild_ids=[878364507385233480])
async def ViewLog(ctx: discord.ApplicationContext, logid: str):
    Pointlog = pointlog.Pointlog.FromID(logid)
    if not Pointlog:
        return await ctx.respond("Log does not exist")

    Pointlog.UpdateEmbed()

    await ctx.respond(embed=Pointlog.Embed)

@bot.command(name="ranklock", description="Ranklock someone", guild_ids=[878364507385233480])
async def RanklockUser(ctx: discord.ApplicationContext, member: discord.Member, setting: bool):
    UserData = points.GetUser(member.id)

    UserData["Ranklocked"] = setting

    points.WriteKey(member.id, UserData)

    await ctx.respond("User ranklocked.")

@bot.command(name="view-consensus", description="View someone's consensus", guild_ids=[878364507385233480])
async def ViewConsensus(ctx: discord.ApplicationContext, member: discord.Member):
    UserData = points.GetUser(member.id)

    if not UserData["Consensus"]:
        return await ctx.respond("User's consensus is empty")

    Embed = discord.Embed(
        description="\n".join(["{}: `{}` - <@{}>".format(UserData["Consensus"].index(Note), Note["Note"], Note["Creator"]) for Note in UserData["Consensus"]]),
        color=0x0452cf
    )
    Embed.set_author(name="United Federation of Planets", icon_url=ctx.guild.icon.url)

    await ctx.respond(embed=Embed)

@bot.command(name="add-consensus", description="Add to someone's consensus", guild_ids=[878364507385233480])
async def AddConsensus(ctx: discord.ApplicationContext, member: discord.Member, note: str):
    UserData = points.GetUser(member.id)

    UserData["Consensus"].append({
        "Note": note,
        "Creator": str(ctx.author.id)
    })

    points.WriteKey(member.id, UserData)

    await ctx.respond("Added to consensus.")

@bot.command(name="remove-consensus", description="Remove an item from someone's consensus", guild_ids=[878364507385233480])
async def RemoveConsensus(ctx: discord.ApplicationContext, member: discord.Member, position: int):
    UserData = points.GetUser(member.id)

    Item = UserData["Consensus"][position]

    UserData["Consensus"].remove(Item)

    points.WriteKey(member.id, UserData)

    await ctx.respond("Removed item from consensus.")

@bot.command(name="clear-consensus", description="Clear someone's consensus", guild_ids=[878364507385233480])
async def ClearConsensus(ctx: discord.ApplicationContext, member: discord.Member):
    UserData = points.GetUser(member.id)

    UserData["Consensus"] = []

    points.WriteKey(member.id, UserData)

    await ctx.respond("Cleared consensus.")

@bot.command(name="create-pointlog", description="Create a pointlog", guild_ids=[878364507385233480])
async def CreatePointlog(ctx: discord.ApplicationContext):
    await ctx.defer()

    PointlogClass = pointlog.Pointlog(ctx)
    PointlogView = pointlog.PointlogView(PointlogClass)

    await ctx.respond(embed=PointlogClass.Embed, view=PointlogView)

    await PointlogView.wait()

    if PointlogView.Cancelled:
        return await ctx.respond("Pointlog cancelled.")

    PointlogChannel = ctx.guild.get_channel(1263658686019141682)

    msg = await PointlogChannel.send("**Pointlog from {}**".format(ctx.author))

    PointlogClass.Log(ctx.author.id, msg.id)
    await msg.edit(embed=PointlogClass.Embed, view=PointlogClass.ToView())

    await ctx.respond("Pointlog awaiting processing...".format(PointlogClass.Key))

@bot.command(name="editmessage", description="Edit a message that UFP Bot has in a channel", guild_ids=[878364507385233480])
async def editmessage(ctx, channel: discord.TextChannel, content: discord.Attachment, borders: bool=False, charterimage: bool = False):
    await ctx.defer()
    fileContent = await content.read()
    fileContent = fileContent.decode("utf-8")
    if len(fileContent) > 2000:
        fileContent = wrapString(fileContent)

    with open("json/channelmessagecache.json", "r") as f:
        data = json.load(f)

    if type(fileContent) == str:
        if (not str(channel.id) in data):
            if borders:
                await channel.send(file=discord.File("LCARS1.png"))
            if charterimage:
                await channel.send(file=discord.File("UFP.png"))
            message = await channel.send(fileContent)
            data[str(channel.id)] = message.id
            if borders:
                await channel.send(file=discord.File("LCARS_Bottom.png"))
            else:
                if borders:
                    await channel.send(file=discord.File("LCARS1.png"))
                if charterimage:
                    await channel.send(file=discord.File("UFP.png"))
                data[str(channel.id)] = []
                for item in fileContent:
                    message = await channel.send(item)
                    data[str(channel.id)].append(message.id)
                if borders:
                    await channel.send(file=discord.File("LCARS_Bottom.png"))
            with open("json/channelmessagecache.json", "w") as f:
                json.dump(data, f, indent=4)
        else:
            try:
                message = await channel.fetch_message(data[str(channel.id)])
                await message.edit(fileContent)
            except:
                if borders:
                    await channel.send(file=discord.File("LCARS1.png"))
                if charterimage:
                    await channel.send(file=discord.File("UFP.png"))
                message = await channel.send(fileContent)
                data[str(channel.id)] = message.id
                if borders:
                    await channel.send(file=discord.File("LCARS_Bottom.png"))
    else:
        if (not str(channel.id) in data):
            if borders:
                await channel.send(file=discord.File("LCARS1.png"))
            if charterimage:
                await channel.send(file=discord.File("UFP.png"))
            data[str(channel.id)] = []
            for item in fileContent:
                message = await channel.send(item)
                data[str(channel.id)].append(message.id)
            if borders:
                await channel.send(file=discord.File("LCARS_Bottom.png"))
        else:
            for messageId in data[str(channel.id)]:
                try:
                    message = await channel.fetch_message(messageId)
                    await message.edit(fileContent[data[str(channel.id)].index(messageId)])
                except:
                    if borders:
                        await channel.send(file=discord.File("LCARS1.png"))
                    if charterimage:
                        await channel.send(file=discord.File("UFP.png"))
                    data[str(channel.id)] = []
                    for item in fileContent:
                        message = await channel.send(item)
                        data[str(channel.id)].append(message.id)
                    if borders:
                        await channel.send(file=discord.File("LCARS_Bottom.png"))



    await ctx.respond("Success")

@bot.command(name="specs", description="Raspberry PI statuses")
async def pispecs(ctx):
    embed = discord.Embed(
        title="PI Status",
        description="CPU Temp: `{}°C` ({}°F)\n\nCPU Usage: `{}%`\nRAM Usage: `{}%`\nDisk Usage: `{}%`".format(CPUTemperature().temperature, (CPUTemperature().temperature * (9/5)) + 32, psutil.cpu_percent(), psutil.virtual_memory().percent, psutil.disk_usage('/').percent)
    )

    await ctx.respond(embed=embed)

@bot.command(name="personnel-report", description="Get a personnel report on a person", guild_ids=[878364507385233480])
async def personnelReport(ctx, member:discord.Member = None):
    await ctx.defer()
    member = member or ctx.author

    data = jsonhandler.getMessageData()
    await member.avatar.save('avatar.png')

    lastMessage = datetime.datetime.fromtimestamp(data[str(member.id)]).strftime("%B %d, %Y") if str(member.id) in data else "None"

    img = Image.new(mode="RGB", size=(720, 520), color=0x000000)
    draw = ImageDraw.Draw(img)

    oswald = ImageFont.truetype("Oswald-Regular.ttf", 30)

    draw.text((320,5), "CREW MANIFEST DATABASE 17834", font=oswald, fill=colors["Bright Purple"])

    draw.rectangle((5, 5, 105, 55), fill=colors["Purple"])
    draw.rectangle((5, 60, 105, 150), fill=colors["Bright Purple"])

    draw.ellipse((5, 130, 105, 175), fill=colors["Bright Purple"])
    draw.rectangle((50, 150, 250, 175), fill=colors["Bright Purple"])
    draw.rectangle((255, 150, 280, 175), fill=colors["Orange"])
    draw.rectangle((285, 150, 395, 175), fill=colors["Blonde"])
    draw.rectangle((400, 150, 650, 175), fill=colors["Purple"])
    draw.rectangle((655, 150, 715, 175), fill=colors["Bright Purple"])

    draw.ellipse((5, 185, 105, 230), fill=colors["Orange"])
    draw.rectangle((50, 185, 250, 210), fill=colors["Orange"])
    draw.rectangle((255, 185, 280, 210), fill=colors["Purple"])
    draw.rectangle((285, 185, 395, 200), fill=colors["Bright Purple"])
    draw.rectangle((400, 185, 650, 210), fill=colors["Blonde"])
    draw.rectangle((655, 185, 715, 210), fill=colors["Orange"])
    draw.rectangle((5, 210, 105, 240), fill=colors["Orange"])

    draw.rectangle((5, 245, 105, 280), fill=colors["Purple"])
    draw.rectangle((5, 285, 105, 370), fill=colors["Blonde"])
    draw.rectangle((5, 375, 105, 410), fill=colors["Orange"])
    draw.rectangle((5, 415, 105, 520), fill=colors["Blonde"])

    oswald = ImageFont.truetype("Oswald-Regular.ttf", 18)

    draw.text((150, 55), "CURRENT RANK: ", font=oswald, fill=colors["Bright Purple"])
    draw.text((260, 55), ranks.getRank(member).name.upper() if ranks.getRank(member) else "None", font=oswald, fill=colors["Orange"])

    draw.text((150, 75), "CURRENT ASSIGNMENT: ", font=oswald, fill=colors["Bright Purple"])
    draw.text((315, 75), ranks.getAssignment(member).name.upper() if ranks.getAssignment(member) else "None", font=oswald, fill=colors["Orange"])

    draw.text((150, 240), "DATE OF JOIN: {}".format(member.joined_at.strftime("%B %d, %Y").upper()), font=oswald, fill=colors["Purple"])
    draw.text((150, 260), "LAST ACTIVITY: {}".format(lastMessage.upper()), font=oswald, fill=colors["Purple"])
    draw.text((150, 280), "STARFLEET MEDALS:", font=oswald, fill=colors["Purple"])
    yVal = 300
    if ranks.getMedals(member):
        for medal in ranks.getMedals(member):
            draw.text((170, yVal), "- {}".format(medal.name), font=oswald, fill=colors["Orange"])

            yVal += 20

    avatar = Image.open('avatar.png').convert("RGB")
    avatar = avatar.resize((220, 220))
    img.paste(avatar, (450, 240))

    img.save("report.png")
    await ctx.respond(file=discord.File("report.png"))

offDuty = bot.create_group("off_duty", "Mark yourself as off duty or extend your duration")

@offDuty.command(name="start", description="AFK command or to tell people ur on vacation", guild_ids=[878364507385233480])
@discord.option("eventtype", description="Type of event that this is.", choices=["AFK", "on Vacation", "Doing Tomfuckery"])
async def offDutyStart(ctx, duration: TimeConverter, eventtype, endwhentext:bool=True, message=None):
    if str(ctx.author.id) in offduty.getUsers():
        return await ctx.respond("You are already marked as off duty")
    
    estimatedEnd = int(duration + datetime.datetime.now().timestamp())

    offduty.addUser(ctx.author.id, estimatedEnd, eventtype, endwhentext, message)

    await ctx.respond("People who ping you will now know that you are offline")

@offDuty.command(name="extend", guild_ids=[878364507385233480])
async def offDutyExtend(ctx, duration: TimeConverter):
    if not str(ctx.author.id) in offduty.getUsers():
        return await ctx.respond("You are not marked as off duty")

    newEnd = offduty.extendUser(ctx.author.id, duration)

    await ctx.respond("Extended your duration to <t:{}:R>".format(newEnd))

@offDuty.command(name="end", guild_ids=[878364507385233480])
async def offDutyEnd(ctx):
    if not str(ctx.author.id) in offduty.getUsers():
        return await ctx.respond("You are not marked as off duty")

    offduty.removeUser(ctx.author.id)

    await ctx.respond("Welcome back.")

@bot.command(name="announce", description="For Captains+", guild_ids=[878364507385233480])
@discord.commands.option("message", description="Use \"\\n\" for a new line")
async def announce(ctx, message, ping:bool=False, publish:bool=False):
    await ctx.defer()
    UFP = await bot.fetch_guild(878364507385233480)
    captain = discord.utils.get(UFP.roles, id=878367800937304146)
    RALH = discord.utils.get(UFP.roles, id=940456287496470578)
    RAUH = discord.utils.get(UFP.roles, id=1022239558093512825)
    VA = discord.utils.get(UFP.roles, id=940456210799411220)
    ADM = discord.utils.get(UFP.roles, id=878367592706887761)
    FADM = discord.utils.get(UFP.roles, id=940455959858413658)
    if (captain in ctx.author.roles) or (RALH in ctx.author.roles) or (RAUH in ctx.author.roles) or (VA in ctx.author.roles) or (ADM in ctx.author.roles) or (FADM in ctx.author.roles):
        channel = await UFP.fetch_channel(878449851833151488)
        message = message.replace("\\n", "\n")

        if ping:
            if not ((VA in ctx.author.roles) or (ADM in ctx.author.roles) or (FADM in ctx.author.roles)):
                ping = False
                await ctx.respond("You need the rank of Vice Admiral to ping", ephemeral=True)

        await channel.send(file=discord.File("LCARS1.png"))
        msg = await channel.send(message + "\n\n`- {} {}`{}".format(await getRank(ctx.author), ctx.author.name, "" if not ping else "\n||<@&954234917846388826>||"), allowed_mentions=discord.AllowedMentions.none() if not ((VA in ctx.author.roles) or (ADM in ctx.author.roles) or (FADM in ctx.author.roles)) else discord.AllowedMentions.all())
        await channel.send(file=discord.File("LCARS_Bottom.png"))

        if publish:
            try:
                await msg.publish()
            except:
                pass

        await ctx.respond("Posted Announcement.", ephemeral=True)
    else:
        await ctx.respond("You do not have atleast the rank of Captain", ephemeral=True)

async def updateRelations():
    UFP = await bot.fetch_guild(878364507385233480)
    channel = await UFP.fetch_channel(924849060270198784)
    try:
        message = await channel.fetch_message(relations.getMessage())
    except:
        message = None
    
    embed = discord.Embed(
        title = "United Federation of Planets Relations",
        description = "# Allies\n``` ```\n{}\n``` ```\n# Friendlies\n``` ```\n{}\n``` ```\n# Enemies\n``` ```\n{}\n\n- Enemies of Allies\n``` ```\n\n**Civilian/Faction ships are neutral**".format("\n".join(["- `{}`".format(ally) for ally in relations.getAllies()]), "\n".join(["- `{}`".format(friendly) for friendly in relations.getFriendlies()]), "\n".join(["- `{}` {}".format(enemy["name"], "**| " + enemy["type"] + "**" if enemy["type"] else "") for enemy in relations.getEnemies().values()]))
    )

    if not message:
        msg = await channel.send("", embed=embed)
        relations.setMessage(msg.id)
    else:
        await message.edit("", embed=embed)

class Relations(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    relations = discord.commands.SlashCommandGroup("relations", "Edit faction relations")

    createRelation = relations.create_subgroup("create", "Create faction relations")
    removeRelation = relations.create_subgroup("remove", "Remove faction relations")

    @relations.command(name="update", description="Update relations", guild_ids=[878364507385233480])
    async def relationsUpdate(self, ctx):
        await ctx.defer()
        await updateRelations()
        await ctx.respond("Updated")

    @createRelation.command(name="ally", description="Add an ally to faction relations", guild_ids=[878364507385233480])
    async def createAlly(self, ctx, faction):
        await ctx.defer()
        result = relations.addAlly(faction)
        relations.removeFriendly(faction)
        relations.removeEnemy(faction)
        if not result:
            return await ctx.respond("This faction is already allied")
        await ctx.respond("Marked this faction as allied")
        await updateRelations()

    @removeRelation.command(name="ally", description="Remove an ally from faction relations", guild_ids=[878364507385233480])
    @discord.commands.option("faction", autocomplete=getAllies)
    async def removeAlly(self, ctx, faction):
        await ctx.defer()
        result = relations.removeAlly(faction)
        if not result:
            return await ctx.respond("This faction is not allied")
        await ctx.respond("Removed this faction from allied list")
        await updateRelations()

    @createRelation.command(name="friendly", description="Add a friendly to faction relations", guild_ids=[878364507385233480])
    async def createFriendly(self, ctx, faction):
        await ctx.defer()
        result = relations.addFriendly(faction)
        relations.removeAlly(faction)
        relations.removeEnemy(faction)
        if not result:
            return await ctx.respond("This faction is already a friendly")
        await ctx.respond("Marked this faction as friendly")
        await updateRelations()

    @removeRelation.command(name="friendly", description="Remove a friendly from faction relations", guild_ids=[878364507385233480])
    @discord.commands.option("faction", autocomplete=getFriendlies)
    async def removeFriendly(self, ctx, faction):
        await ctx.defer()
        result = relations.removeFriendly(faction)
        if not result:
            return await ctx.respond("This faction is not a friendly")
        await ctx.respond("Removed this faction from friendly list")
        await updateRelations()

    @createRelation.command(name="enemy", description="Add an enemy to faction relations", guild_ids=[878364507385233480])
    @discord.commands.option("enemytype", autocomplete=getTypes)
    async def createEnemy(self, ctx, entity, enemytype):
        await ctx.defer()
        result = relations.addEnemy(entity, enemytype)
        relations.removeAlly(entity)
        relations.removeFriendly(entity)
        if not result:
            return await ctx.respond("This entity is already an enemy")
        await ctx.respond("Marked this entity as an enemy")
        await updateRelations()

    @removeRelation.command(name="enemy", description="Remove an enemy from faction relations", guild_ids=[878364507385233480])
    @discord.commands.option("entity", autocomplete=getEnemies)
    async def removeEnemy(self, ctx, entity):
        await ctx.defer()
        result = relations.removeEnemy(entity)
        if not result:
            return await ctx.respond("This entity is not an enemy")
        await ctx.respond("Removed this entity from enemy list")
        await updateRelations()

bot.add_cog(Relations(bot))

@bot.command(name="srads", description="For Admirals+ | Sets SRADS Level and Sets Up Server Accordingly", guild_ids=[878364507385233480])
async def setSrads(ctx, level:int):
    UFP = await bot.fetch_guild(878364507385233480)
    captain = discord.utils.get(UFP.roles, id=878367800937304146)
    RALH = discord.utils.get(UFP.roles, id=940456287496470578)
    RAUH = discord.utils.get(UFP.roles, id=1022239558093512825)
    VA = discord.utils.get(UFP.roles, id=940456210799411220)
    ADM = discord.utils.get(UFP.roles, id=878367592706887761)
    FADM = discord.utils.get(UFP.roles, id=940455959858413658)
    restricted = discord.utils.get(UFP.roles, id=1122368049157255180)
    commissioned = discord.utils.get(UFP.roles, id=954234917846388826)
    ambassador = discord.utils.get(UFP.roles, id=897176672825143296)

    if 1 <= level <= 5 or level != srads.getLevel():
        await ctx.defer()

        if level == 5:
            if srads.getLevel() <= 4:
                for member in ctx.guild.members:
                    if restricted in member.roles:
                        await member.remove_roles(restricted)
                        await member.add_roles(commissioned)
            
            if srads.getLevel() <= 3:
                wartimeChannel = await UFP.fetch_channel(srads.getWartimeChannel())
                await wartimeChannel.delete()
        else:
            if level == 3:
                overwrites = {
                    UFP.default_role: discord.PermissionOverwrite(view_channel=False),
                    captain: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                    RALH: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                    RAUH: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                    VA: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                    ADM: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                    FADM: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                    commissioned: discord.PermissionOverwrite(view_channel=True, send_messages=False),
                    restricted: discord.PermissionOverwrite(view_channel=False),
                    ctx.guild.me: discord.PermissionOverwrite(view_channel=True)
                }

                category = await UFP.fetch_channel(878364509205581854)
                wartimeChannel = await category.create_text_channel("wartime-announcements", overwrites=overwrites, position=2)
                srads.setWartimeChannel(wartimeChannel.id)

            if level < 3:
                if srads.getLevel() > 3:
                    overwrites = {
                        UFP.default_role: discord.PermissionOverwrite(view_channel=False),
                        commissioned: discord.PermissionOverwrite(view_channel=True),
                        restricted: discord.PermissionOverwrite(view_channel=False),
                        ctx.guild.me: discord.PermissionOverwrite(view_channel=True)
                    }

                    category = await UFP.fetch_channel(878364509205581854)
                    wartimeChannel = await category.create_text_channel("wartime-announcements", overwrites=overwrites, position=2)
                    srads.setWartimeChannel(wartimeChannel.id)

        srads.setLevel(level)
        await ctx.respond("All protocols for `SRADS {}` engaged.".format(level))

        messages = {
            "5": "The Federation is at no threat and no special action is being taken.",
            "4": "The Federation has increased attention on other factions and strengthened security. Officers affiliated to those who caused this will experience decreased access in the server.",
            "3": "The Federation is above normal readiness, task-forces are deployed, and <@&958097146761084958> is in full activation. <#{}> is opened to unrestricted commissioned personnel".format(srads.getWartimeChannel()),
            "2": "The Federation is in danger, all personnel are ready to deploy. ( <@&946227554136764416> personnel are asked to become active.)",
            "1": "The Federation's very existence is at threat, maximum readiness is in effect."
        }

        channel = await UFP.fetch_channel(878449851833151488)
        await channel.send(file=discord.File("LCARS1.png"))
        await channel.send("||<@&954234917846388826>|| `Admiral {}` has initiated SRADS {}\n\n{}".format(ctx.author.name, level, messages[str(level)]))
        await channel.send(file=discord.File("LCARS_Bottom.png"))
    else:
        await ctx.respond("Invalid SRADS Level")

@bot.command(name="server", description="See the member count", guild_ids=[878364507385233480])
async def serverInfo(ctx):
    await ctx.defer()

    UFP = await bot.fetch_guild(878364507385233480)
    active = 0
    reserve = 0
    commissioned = 0
    visitor = 0
    ambassador = 0
    roles = {
        "c": discord.utils.get(UFP.roles, id=954234917846388826),
        "r": discord.utils.get(UFP.roles, id=946227554136764416),
        "v": discord.utils.get(UFP.roles, id=954904188733767721),
        "a": discord.utils.get(UFP.roles, id=897176672825143296)
    }
    for member in ctx.guild.members:
        if roles["c"] in member.roles:
            if roles["r"] in member.roles:
                reserve += 1
            else:
                active += 1
            commissioned += 1
        elif roles["v"] in member.roles:
            if roles["a"] in member.roles:
                ambassador += 1
            visitor += 1
    
    embed = discord.Embed(
        title="United Federation of Planets Members",
        description="- Commissioned Personnel: `{}`\n  - Active: `{}`\n  - Reserve: `{}`\n- Visitors: `{}`\n  - Ambassadors: `{}`".format(commissioned, active, reserve, visitor, ambassador)
    )

    memberData = jsonhandler.getActivity()

    df = pd.DataFrame({
        "Days": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30],
        "Total": memberData["total"],
        "Total Commissioned": memberData["totalCommed"],
        "Active Commissioned": memberData["activeCommed"],
        "Reserved Commissioned": memberData["reserveCommed"],
        "Visitors": memberData["visitors"],
        "Ambassadors": memberData["ambassadors"]
    })

    fig = px.line(df, x="Days", y=["Total", "Total Commissioned", "Active Commissioned", "Reserved Commissioned", "Visitors", "Ambassadors"], title="Member Activity")
    fig.update_traces(
        showlegend=True
    )

    fig.update_layout(
        template='plotly_dark',
        yaxis_title='Member Count'
    )

    fig.write_image("utility/chart.png")

    await ctx.respond(embed=embed, file=discord.File("utility/chart.png"))

@bot.command(name="edit", description="For Captains+ | Edit announcement message", guild_ids=[878364507385233480])
@discord.commands.option("message", description="Use \"\\n\" for a new line")
async def announceEdit(ctx, messageid, message, publish:bool=False):
    messageid = int(messageid)
    UFP = await bot.fetch_guild(878364507385233480)
    captain = discord.utils.get(UFP.roles, id=878367800937304146)
    RALH = discord.utils.get(UFP.roles, id=940456287496470578)
    RAUH = discord.utils.get(UFP.roles, id=1022239558093512825)
    VA = discord.utils.get(UFP.roles, id=940456210799411220)
    ADM = discord.utils.get(UFP.roles, id=878367592706887761)
    FADM = discord.utils.get(UFP.roles, id=940455959858413658)
    if (captain in ctx.author.roles) or (RALH in ctx.author.roles) or (RAUH in ctx.author.roles) or (VA in ctx.author.roles) or (ADM in ctx.author.roles) or (FADM in ctx.author.roles):
        channel = await UFP.fetch_channel(878449851833151488)
        message = message.replace("\\n", "\n")

        msg = await channel.fetch_message(messageid)
        await msg.edit(message + "\n\n`- {} {}`".format(await getRank(ctx.author), ctx.author.name))

        if publish:
            try:
                await msg.publish()
            except:
                pass

        await ctx.respond("Posted Announcement.", ephemeral=True)
    else:
        await ctx.respond("You do not have atleast the rank of Captain", ephemeral=True)

@bot.command(name="balance", description="Check your amoung of latinum", guild_ids=[878364507385233480])
async def balance(ctx, member:discord.Member=None):
    data = jsonhandler.getAccount(member or ctx.author)

    embed = discord.Embed(
        title="{}'s Balance".format(member or ctx.author),
        description="- Latinum:\n  - Bars: {val1:,}\n  - Strips: {val2:,}\n  - Slips: {val3:,}".format(val1=data["latinum"]["bars"], val2=data["latinum"]["strips"], val3=data["latinum"]["slips"])
    )

    await ctx.respond(embed=embed)

@bot.command(name="exchange", description="Exchange your latinum for different pieces of latinum", guild_ids=[878364507385233480])
@discord.commands.option("latinumfrom", autocomplete=getLatinumTypes)
@discord.commands.option("latinumto", autocomplete=getLatinumTypes)
async def exchangeLatinum(ctx, latinumfrom, latinumto, amount:int=None):
    if not ((latinumfrom.lower() in latinumTypesLower) and (latinumto.lower() in latinumTypesLower)):
        return await ctx.respond("Invalid latinum type")

    data = jsonhandler.getAccount(ctx.author)
    amount = amount or data["latinum"][latinumfrom.lower()]

    if amount <= 0:
        return await ctx.respond("Invalid latinum amount")

    if amount > data["latinum"][latinumfrom.lower()]:
        return await ctx.respond("You do not have this much latinum")

    jsonhandler.removeLatinum(ctx.author, latinumfrom.lower(), int(amount * exchanges[latinumfrom.lower()][latinumto.lower()]) * exchanges[latinumto.lower()][latinumfrom.lower()])
    jsonhandler.addLatinum(ctx.author, latinumto.lower(), int(amount * exchanges[latinumfrom.lower()][latinumto.lower()]))

    await ctx.respond("Done.")

@bot.command(name="share", description="Scam people or graciously give latinum to people", guild_ids=[878364507385233480])
@discord.commands.option("latinumtype", autocomplete=getLatinumTypes)
async def shareLatinum(ctx, latinumtype, amount:int, member:discord.Member):
    if not latinumtype.lower() in latinumTypesLower:
        return await ctx.respond("Invalid latinum type")

    if amount <= 0:
        return await ctx.respond("Invalid latinum amount")

    data = jsonhandler.getAccount(ctx.author)

    if amount > data["latinum"][latinumtype.lower()]:
        return await ctx.respond("You do not have this much latinum")

    memberdata = jsonhandler.getAccount(member)

    jsonhandler.removeLatinum(ctx.author, latinumtype.lower(), amount)
    jsonhandler.addLatinum(member, latinumtype.lower(), amount)

    await ctx.respond("Successfully transferred")

@bot.command(name="leaderboard", description="Find out who is the richest in latinum", guild_ids=[878364507385233480])
async def leaderboardLatinum(ctx):
    networths = jsonhandler.getNetworths()
    leaderboard = sorted(networths, key=lambda x: x["networth"], reverse=True)

    em = discord.Embed(
        title="Top 10 richest users"
    )
    index = 0
    for user in leaderboard:
        if index == 10 or index == len(leaderboard):
            break
        else:
            index += 1
            em.add_field(name=f"{index}. {await bot.fetch_user(user['member'])}", value=f"{user['networth']:,} Bars", inline=False)

    await ctx.respond(embed=em)

@bot.command(name="slots", description="Win some latinum", guild_ids=[878364507385233480])
@discord.commands.option("latinumtype", autocomplete=getLatinumTypes)
async def slotsGame(ctx, latinumtype, amount:int):
    if not latinumtype.lower() in latinumTypesLower:
        return await ctx.respond("Invalid latinum type")

    if amount <= 0:
        return await ctx.respond("Invalid latinum amount")

    data = jsonhandler.getAccount(ctx.author)

    if amount > data["latinum"][latinumtype.lower()]:
        return await ctx.respond("You do not have this much latinum")

    jsonhandler.removeLatinum(ctx.author, latinumtype.lower(), amount)

    multi = 1

    emojis = ["🍎", "🍋", "🍌", "🍆", "🍒", "🍇", "🍊"]

    slot1 = random.choice(emojis)
    slot2 = random.choice(emojis)
    slot3 = random.choice(emojis)

    if data["thing"] and ctx.author.id == 485513915548041239:
        choice = random.choice([1, 2])

        if choice == 1:
            slot2 = slot1
        elif choice == 2:
            slot3 = slot1

    embed = discord.Embed(
        title = "Slots Game",
        description = "{} {} {}".format(slot1, slot2, slot3),
        color = 0xff0000
    )

    if slot1 == slot2 and slot2 == slot3 and slot1 == slot3:
        multi = 2
        embed.color = 0x00ff00
    elif slot1 == slot2 and slot2 != slot3 and slot1 != slot3:
        multi = 1.5
        embed.color = 0x00ff00
    elif slot1 != slot2 and slot2 == slot3 and slot1 != slot3:
        multi = 1.5
        embed.color = 0x00ff00
    elif slot1 != slot2 and slot2 != slot3 and slot1 == slot3:
        multi = 1.5
        embed.color = 0x00ff00

    if multi > 1:
        embed.description += "\n\n**{}x** of your original bet won".format(multi)

        jsonhandler.addLatinum(ctx.author, latinumtype.lower(), int(amount * (multi + 1)))

    data = jsonhandler.getAccount(ctx.author)
    
    embed.description += "\n\nBalance:\n- Latinum:\n  - Bars: {val1:,}\n  - Strips: {val2:,}\n  - Slips: {val3:,}".format(val1=data["latinum"]["bars"], val2=data["latinum"]["strips"], val3=data["latinum"]["slips"])

    await ctx.respond(embed=embed)

@bot.command(name="snakeeyes", description="Win some latinum", guild_ids=[878364507385233480])
@discord.commands.option("latinumtype", autocomplete=getLatinumTypes)
async def snakeeyesGame(ctx, latinumtype, amount:int):
    if not latinumtype.lower() in latinumTypesLower:
        return await ctx.respond("Invalid latinum type")

    if amount <= 0:
        return await ctx.respond("Invalid latinum amount")

    data = jsonhandler.getAccount(ctx.author)

    if amount > data["latinum"][latinumtype.lower()]:
        return await ctx.respond("You do not have this much latinum")

    dice = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]

    dice1 = random.choice(dice)
    dice2 = random.choice(dice)

    jsonhandler.removeLatinum(ctx.author, latinumtype.lower(), amount)

    multi = 1

    embed = discord.Embed(
        title = "Snake Eyes Game",
        description = "**{} {}**".format(dice1, dice2),
        color = 0xff0000
    )

    if dice1 == "⚀":
        multi += 0.5
        embed.color = 0x00ff00
    if dice2 == "⚀":
        multi += 0.5
        embed.color = 0x00ff00

    if multi > 1:
        embed.description += "\n\n**{}x** of your original bet won".format(multi)

        jsonhandler.addLatinum(ctx.author, latinumtype.lower(), int(amount * (multi + 1)))

    data = jsonhandler.getAccount(ctx.author)
    
    embed.description += "\n\nBalance:\n- Latinum:\n  - Bars: {val1:,}\n  - Strips: {val2:,}\n  - Slips: {val3:,}".format(val1=data["latinum"]["bars"], val2=data["latinum"]["strips"], val3=data["latinum"]["slips"])

    await ctx.respond(embed=embed)

@bot.command(name="blackjack", description="Win some latinum", guild_ids=[878364507385233480])
@discord.commands.option("latinumtype", autocomplete=getLatinumTypes)
async def blackjackGame(ctx, latinumtype, amount:int):
    if not latinumtype.lower() in latinumTypesLower:
        return await ctx.respond("Invalid latinum type")

    if amount <= 0:
        return await ctx.respond("Invalid latinum amount")

    data = jsonhandler.getAccount(ctx.author)

    if amount > data["latinum"][latinumtype.lower()]:
        return await ctx.respond("You do not have this much latinum")

    jsonhandler.removeLatinum(ctx.author, latinumtype.lower(), amount)

    view = blackjack.Blackjack(ctx, data)
    embed = discord.Embed(
        title="Blackjack Game",
        description=""
    )
    embed.add_field(name="Your Cards ({})".format(blackjack.getValue(view.playerCards)), value=", ".join(view.playerCards))
    embed.add_field(name="Bot's Cards", value=view.botCards[0] + ", " + ", ".join(["?" for i in range(len(view.botCards[1:]))]))

    msg = await ctx.respond(embed=embed, view=view)

    await view.wait()

    embed.clear_fields()
    embed.add_field(name="Your Cards ({})".format(blackjack.getValue(view.playerCards)), value=", ".join(view.playerCards))
    embed.add_field(name="Bot's Cards ({})".format(blackjack.getValue(view.botCards)), value=", ".join(view.botCards))

    embed.description = view.reason

    if view.result:
        embed.color = 0x00ff00

        jsonhandler.addLatinum(ctx.author, latinumtype.lower(), amount * 2)
    elif view.result == False:
        embed.color = 0xff0000
    elif view.result == None:
        embed.color = 0xffff00

        jsonhandler.addLatinum(ctx.author, latinumtype.lower(), amount)

    data = jsonhandler.getAccount(ctx.author)
    embed.description += "\n\nBalance:\n- Latinum:\n  - Bars: {val1:,}\n  - Strips: {val2:,}\n  - Slips: {val3:,}".format(val1=data["latinum"]["bars"], val2=data["latinum"]["strips"], val3=data["latinum"]["slips"])

    await msg.edit_original_response(embed=embed, view=view)

@bot.command(name="free", description="Only works if you are broke", guild_ids=[878364507385233480])
async def freeLatinum(ctx):
    data = jsonhandler.getAccount(ctx.author)

    if data["latinum"]["bars"] == 0 and data["latinum"]["strips"] == 0 and data["latinum"]["slips"] == 0:
        jsonhandler.addLatinum(ctx.author, "strips", 10)

        await ctx.respond("You are now not broke")
    else:
        await ctx.respond("Bruh ur not broke")

shopGroup = bot.create_group("shop", "Buy some ships or equipment")

@shopGroup.command(name="ships", description="Buy some ships", guild_ids=[878364507385233480])
async def shipShop(ctx):
    embed = discord.Embed(
        title="Ship Shop",
        description=""
    )
    enums = {
        "1": "Common",
        "2": "Uncommon",
        "3": "Rare",
        "4": "Epic",
        "5": "Legendary",
        "6": "Mythic"
    }

    for item in ships.shop:
        embed.description += '**[{}]** `{}` —— **{cost:,d}** Bars of Gold-Pressed Latinum\n- {tier}x All Stats\n\n'.format(enums[str(item["tier"])], item["name"], cost=item["cost"], tier=item["tier"])

    await ctx.respond(embed=embed, view=ships.Interface(ctx))

@shopGroup.command(name="equipment", description="Buy some ship equipment", guild_ids=[878364507385233480])
async def equipmentShop(ctx):
    embed = discord.Embed(
        title="Ship Equipment Shop",
        description="\n".join(upgrades.shop.keys())
    )
    
    await ctx.respond(embed=embed, view=upgrades.Interface(ctx))

@bot.command(name="ship", description="Look at ur ship stats", guild_ids=[878364507385233480])
async def shipView(ctx):
    data = jsonhandler.getAccount(ctx.author)

    if not data["equipped"]:
        return await ctx.respond("You do not have a ship equipped")

    enums = {
        "1": "Common",
        "2": "Uncommon",
        "3": "Rare",
        "4": "Epic",
        "5": "Legendary",
        "6": "Mythic"
    }

    def getFormat(argone, argtwo, part):
        return [data["equipped"][argone], 0 if not data["equipped"]["equipment"][argtwo] else data["equipped"]["equipment"][argtwo]["capacity"] * (data["equipped"]["tier"] if argtwo in ["sif", "sg"] else 1), "" if (not data["equipped"]["equipment"][argtwo]) or ((data["equipped"]["equipment"][argtwo]["capacity"] if argtwo not in ["sg", "sif"] else data["equipped"]["equipment"][argtwo]["capacity"] * data["equipped"]["tier"]) == data["equipped"][argone] or data["equipped"]["equipment"][argtwo]["tier"] == "MK I") else "**{} Bars of Latinum to {}**".format(int(((data["equipped"]["equipment"][argtwo]["capacity"] if argtwo not in ["sg", "sif"] else data["equipped"]["equipment"][argtwo]["capacity"] * data["equipped"]["tier"]) - data["equipped"][argone]) / (10 if argone != "deuterium" else 1)), part)]

    embed = discord.Embed(
        title=data["equipped"]["name"],
        description="Tier: **{}**\nDeuterium: `{}/{}` {}\nHull: `{}/{}` {}\nShields: `{}/{}` {}\n\n**Shield Generators:** `{}`\n**Structural Integrity Fields:** `{}`\n**Phasers:** `{}`\n**Torpedo Launchers:** `{}`\n**Deuterium Tanks:** `{}`".format(enums[str(data["equipped"]["tier"])], getFormat("deuterium", "dt", "fill")[0], getFormat("deuterium", "dt", "fill")[1], getFormat("deuterium", "dt", "fill")[2], getFormat("hull", "sif", "repair")[0], getFormat("hull", "sif", "repair")[1], getFormat("hull", "sif", "repair")[2], getFormat("shields", "sg", "repair")[0], getFormat("shields", "sg", "repair")[1], getFormat("shields", "sg", "repair")[2], data["equipped"]["equipment"]["sg"]["tier"] if data["equipped"]["equipment"]["sg"] else None, data["equipped"]["equipment"]["sif"]["tier"] if data["equipped"]["equipment"]["sif"] else None, data["equipped"]["equipment"]["p"]["tier"] if data["equipped"]["equipment"]["p"] else None, data["equipped"]["equipment"]["tl"]["tier"] if data["equipped"]["equipment"]["tl"] else None, data["equipped"]["equipment"]["dt"]["tier"] if data["equipped"]["equipment"]["dt"] else None)
    )
    await ctx.respond(embed=embed)

equipGroup = bot.create_group("equip", "Equip ships or equipment")

@equipGroup.command(name="ship", description="Equip a ship", guild_ids=[878364507385233480])
async def equipShip(ctx):
    data = jsonhandler.getAccount(ctx.author)

    embed = discord.Embed(
        title="Ship Roster",
        description=""
    )
    enums = {
        "1": "Common",
        "2": "Uncommon",
        "3": "Rare",
        "4": "Epic",
        "5": "Legendary",
        "6": "Mythic"
    }

    if data["ships"]:
        for item in data["ships"].values():
            embed.description += '**[{}]** `{}`\n'.format(enums[str(item["tier"])], item["name"])
    else:
        embed.description = "No Ships"

    await ctx.respond(embed=embed, view=ships.EquipInterface(ctx) if data["ships"] else None)

@equipGroup.command(name="equipment", description="Equip equipment on your ship", guild_ids=[878364507385233480])
async def equipEquipment(ctx):
    data = jsonhandler.getAccount(ctx.author)
    if not data["equipped"]:
        return await ctx.respond("You do not have a ship equipped")

    embed = discord.Embed(
        title="Ship Equipment Roster",
        description="\n".join(upgrades.shop.keys())
    )
    
    await ctx.respond(embed=embed, view=upgrades.EquipInterface(ctx))

@bot.command(name="repair", description="Repair your ship", guild_ids=[878364507385233480])
async def repairShip(ctx):
    data = jsonhandler.getAccount(ctx.author)
    if not data["equipped"]:
        return await ctx.respond("You do not have a ship equipped")

    totalCost = 0
    totalCost += 0 if (not data["equipped"]["equipment"]["dt"]) or data["equipped"]["equipment"]["dt"]["tier"] == "MK I" else int((data["equipped"]["equipment"]["dt"]["capacity"] - data["equipped"]["deuterium"]))
    totalCost += 0 if (not data["equipped"]["equipment"]["sg"]) or data["equipped"]["equipment"]["sg"]["tier"] == "MK I" else int((((data["equipped"]["equipment"]["sg"]["capacity"] * data["equipped"]["tier"]) - data["equipped"]["shields"]) / 10))
    totalCost += 0 if (not data["equipped"]["equipment"]["sif"]) or data["equipped"]["equipment"]["sif"]["tier"] == "MK I" else int((((data["equipped"]["equipment"]["sif"]["capacity"] * data["equipped"]["tier"]) - data["equipped"]["hull"]) / 10))

    if data["latinum"]["bars"] < totalCost:
        return await ctx.respond("You need {} bars of latinum to repair your ship".format(totalCost))

    jsonhandler.removeLatinum(ctx.author, "bars", totalCost)
    jsonhandler.setShipAttribute(ctx.author, "deuterium", 0 if not data["equipped"]["equipment"]["dt"] else data["equipped"]["equipment"]["dt"]["capacity"])
    jsonhandler.setShipAttribute(ctx.author, "shields", 0 if not data["equipped"]["equipment"]["sg"] else data["equipped"]["equipment"]["sg"]["capacity"] * data["equipped"]["tier"])
    jsonhandler.setShipAttribute(ctx.author, "hull", 0 if not data["equipped"]["equipment"]["sif"] else data["equipped"]["equipment"]["sif"]["capacity"] * data["equipped"]["tier"])
    await ctx.respond("Successfully repaired")

@bot.command(name="autorepair", description="Setup auto-repair for after debris scrounging", guild_ids=[878364507385233480])
async def autoRepair(ctx, setting:bool):
    data = jsonhandler.getAccount(ctx.author)
    jsonhandler.setSetting(ctx.author, setting)

    await ctx.respond("Successfully changed setting")

@bot.command(name="debris", description="Scrounge through debris", guild_ids=[878364507385233480])
async def debris(ctx):
    await ctx.defer()
    data = jsonhandler.getAccount(ctx.author)
    if not data["equipped"]:
        return await ctx.respond("You do not have a ship equipped")

    if data["equipped"]["deuterium"] == 0:
        return await ctx.respond("Your ship has no deuterium")
    
    if data["equipped"]["hull"] == 0:
        return await ctx.respond("Your ship has been destroyed")

    earnings = {
        "latinum": {
            "bars": 0,
            "strips": 0,
            "slips": 0
        }
    }

    enemyCount = 0

    message = ""

    for i in range(data["equipped"]["deuterium"]):
        data["equipped"]["deuterium"] -= 1
        roll = random.randrange(0, 100)
        table = {
            "MK I": 1,
            "MK II": 2,
            "MK III": 3,
            "MK IV": 4,
            "MK V": 5,
            "MK VI": 6,
            "MK VII": 7,
            "MK VIII": 8,
            "MK IX": 9,
            "MK X": 10,
            "MK XI": 11,
            "MK XII": 12,
            "MK XIII": 13,
            "MK XIV": 14,
            "MK XV": 15
        }

        if 0 <= roll <= 20:
            totalDamage = (0 if not data["equipped"]["equipment"]["p"] else data["equipped"]["equipment"]["p"]["damage"]) + (0 if not data["equipped"]["equipment"]["tl"] else data["equipped"]["equipment"]["tl"]["damage"])
            
            enemyCount += 1
            enemy = {
                "shields": 200 if not data["equipped"]["equipment"]["sg"] else data["equipped"]["equipment"]["sg"]["capacity"] / (table[data["equipped"]["equipment"]["sg"]["tier"]] * 5),
                "hull": data["equipped"]["equipment"]["sif"]["capacity"] / (table[data["equipped"]["equipment"]["sif"]["tier"]] * 5),
                "damage": int(25 if not totalDamage else totalDamage / (((table[data["equipped"]["equipment"]["sif"]["tier"]] + table[data["equipped"]["equipment"]["sg"]["tier"]]) / 2) * (random.randrange(10, 25) / 10)))
            }

            while enemy["hull"] > 0 and data["equipped"]["hull"] > 0:

                if enemy["shields"] > 0:
                    enemy["shields"] -= totalDamage
                else:
                    enemy["hull"] -= totalDamage
                
                if enemy["hull"] > 0:
                    if data["equipped"]["shields"] > 0:
                        data["equipped"]["shields"] -= enemy["damage"]
                        if data["equipped"]["shields"] < 0:
                            data["equipped"]["shields"] = 0
                    else:
                        data["equipped"]["hull"] -= enemy["damage"]
                        if data["equipped"]["hull"] < 0:
                            data["equipped"]["hull"] = 0
            
            if data["equipped"]["hull"] <= 0:
                message = "Ship has been destroyed"
                break
        elif 21 <= roll <= 50:
            deuterium = table[data["equipped"]["equipment"]["dt"]["tier"]]

            latinumRoll = random.randrange(0, 100)

            if 0 <= latinumRoll <= 20:
                latinumAmount = random.randrange(5, 50)

                earnings["latinum"]["bars"] += int(latinumAmount * data["equipped"]["tier"] * (data["equipped"]["hull"] / (data["equipped"]["equipment"]["sif"]["capacity"])) * (1 + (deuterium / 2)))
            elif 21 <= latinumRoll <= 50:
                latinumAmount = random.randrange(5, 50)

                earnings["latinum"]["strips"] += int(latinumAmount * data["equipped"]["tier"] * (data["equipped"]["hull"] / (data["equipped"]["equipment"]["sif"]["capacity"])) * (1 + (deuterium / 2)))
            elif 51 <= latinumRoll <= 100:
                latinumAmount = random.randrange(5, 500)

                earnings["latinum"]["slips"] += int(latinumAmount * data["equipped"]["tier"] * (data["equipped"]["hull"] / (data["equipped"]["equipment"]["sif"]["capacity"])) * (1 + (deuterium / 2)))

    jsonhandler.setShipAttribute(ctx.author, "deuterium", data["equipped"]["deuterium"])
    jsonhandler.setShipAttribute(ctx.author, "hull", data["equipped"]["hull"])
    jsonhandler.setShipAttribute(ctx.author, "shields", data["equipped"]["shields"])

    jsonhandler.addLatinum(ctx.author, "bars", earnings["latinum"]["bars"])
    jsonhandler.addLatinum(ctx.author, "strips", earnings["latinum"]["strips"])
    jsonhandler.addLatinum(ctx.author, "slips", earnings["latinum"]["slips"])

    repaired = False

    if data["thing"]:
        data = jsonhandler.getAccount(ctx.author)
        if not data["equipped"]:
            return await ctx.respond("You do not have a ship equipped")

        totalCost = 0
        totalCost += 0 if (not data["equipped"]["equipment"]["dt"]) or data["equipped"]["equipment"]["dt"]["tier"] == "MK I" else int((data["equipped"]["equipment"]["dt"]["capacity"] - data["equipped"]["deuterium"]))
        totalCost += 0 if (not data["equipped"]["equipment"]["sg"]) or data["equipped"]["equipment"]["sg"]["tier"] == "MK I" else int((((data["equipped"]["equipment"]["sg"]["capacity"] * data["equipped"]["tier"]) - data["equipped"]["shields"]) / 10))
        totalCost += 0 if (not data["equipped"]["equipment"]["sif"]) or data["equipped"]["equipment"]["sif"]["tier"] == "MK I" else int((((data["equipped"]["equipment"]["sif"]["capacity"] * data["equipped"]["tier"]) - data["equipped"]["hull"]) / 10))

        if data["latinum"]["bars"] < totalCost:
            await ctx.respond("You need {} bars of latinum to repair your ship".format(totalCost))

        else:
            jsonhandler.removeLatinum(ctx.author, "bars", totalCost)
            jsonhandler.setShipAttribute(ctx.author, "deuterium", 0 if not data["equipped"]["equipment"]["dt"] else data["equipped"]["equipment"]["dt"]["capacity"])
            jsonhandler.setShipAttribute(ctx.author, "shields", 0 if not data["equipped"]["equipment"]["sg"] else data["equipped"]["equipment"]["sg"]["capacity"] * data["equipped"]["tier"])
            jsonhandler.setShipAttribute(ctx.author, "hull", 0 if not data["equipped"]["equipment"]["sif"] else data["equipped"]["equipment"]["sif"]["capacity"] * data["equipped"]["tier"])
            repaired = True

    await ctx.respond(message + ("\n\n" if message else "") + "Enemies Encountered: {}\nTotal Earnings:\n\n- Latinum\n  - Bars: {}\n  - Strips: {}\n  - Slips: {}{}".format(enemyCount, earnings["latinum"]["bars"], earnings["latinum"]["strips"], earnings["latinum"]["slips"], "\n\nSuccessfully repaired" if repaired else ""))

@bot.command(description="restart")
async def restart(ctx: discord.ApplicationContext, gitpull: bool = False):
    if not ctx.author.id == 485513915548041239:
        return
    
    msg = await ctx.respond("Pulling from github repository...")
    if gitpull:
        os.system("git pull")
    await msg.edit_original_response(content="Restarting...")
    try:
        requests.get("http://localhost:6060/ubdc")
    except:
        pass
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command(description="Bot Owner use only")
async def run(ctx, *, cmd):
    whitelist = [485513915548041239]
    if ctx.author.id not in whitelist:
        return
    fn_name = "_eval_expr"
    cmd = cmd.strip("` ")
    cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
    body = f"async def {fn_name}():\n{cmd}"
    parsed = ast.parse(body)
    body = parsed.body[0].body
    insert_returns(body)
    env = {
        'bot': bot,
        'guild': ctx.guild,
        'author': ctx.author,
        'channel': ctx.channel,
        'os': os,
        'discord': discord,
        'ctx': ctx,
        '__import__': __import__,
        'py': None
    }
    try:
        exec(compile(parsed, filename="<ast>", mode="exec"), env)
        result = (await eval(f"{fn_name}()", env))
        if type(result) == discord.Message:
            return
        await ctx.respond(result)
    except Exception:
        await ctx.respond(traceback.format_exc(),delete_after=10)

def mentionedTask():
    while True:
        if bot.mentioned:
            asyncio.run(asyncio.sleep(10))
            bot.mentioned = False

@bot.event
async def on_member_update(before, after):
    UFP = await bot.fetch_guild(878364507385233480)
    await commandingOfficers.updateCommandingOfficers(bot, UFP)

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        w, d = divmod(d, 7)
        em = discord.Embed(color=0xff0000)
        if int(d) == 0 and int(h) == 0 and int(m) == 0:
            em.set_author(
                name=f' You must wait {int(s)} seconds to use this command'
            )
        elif int(d) == 0 and int(h) == 0:
            em.set_author(
                name=
                f' You must wait {int(m)} minutes and {int(s)} seconds to use this command'
            )
        elif int(d) == 0 and int(m) != 0:
            em.set_author(
                name=
                f' You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command'
            )
        elif int(d) != 0 and int(h) != 0 and int(m) != 0:
            em.set_author(
                name=
                f' You must wait {int(d)} days, {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command'
            )
        else:
            em.set_author(
                name=
                f' You must wait {int(w)} weeks, {int(d)} days, {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command'
            )
        await ctx.respond(embed=em, ephemeral=True)
    else:
        await ctx.respond("The bot had the following error: \n```\n{}\n```".format("".join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))), ephemeral=True)

@tasks.loop(minutes=60)
async def reserveTask():
    UFP = await bot.fetch_guild(878364507385233480)
    await commandingOfficers.updateCommandingOfficers(bot, UFP)
    roles = {
        "c": discord.utils.get(UFP.roles, id=954234917846388826),
        "r": discord.utils.get(UFP.roles, id=946227554136764416)
    }
    data = jsonhandler.getMessageData()

    firstFleet = discord.utils.get(UFP.roles, id=958097146761084958)
    secondFleet = discord.utils.get(UFP.roles, id=958097259201957928)
    thirdFleet = discord.utils.get(UFP.roles, id=958097325299990621)
    async def remove_fleet_except(member, role):
        if role:
            if role != firstFleet and firstFleet in member.roles:
                await member.remove_roles(firstFleet)
            if role != secondFleet and secondFleet in member.roles:
                await member.remove_roles(secondFleet)
            if role != thirdFleet and thirdFleet in member.roles:
                await member.remove_roles(thirdFleet)
            if not role in member.roles:
                await member.add_roles(role)
        else:
            if firstFleet in member.roles:
                await member.remove_roles(firstFleet)
            if secondFleet in member.roles:
                await member.remove_roles(secondFleet)
            if thirdFleet in member.roles:
                await member.remove_roles(thirdFleet)

    async for member in UFP.fetch_members(limit=1000):
        if roles["c"] in member.roles:
            if not str(member.id) in data or int(datetime.datetime.now().timestamp()) - data[str(member.id)] >= time_dict["d"] * (7 if member.id != 485513915548041239 else 2):
                if not roles["r"] in member.roles:
                    await member.add_roles(roles["r"], reason=None if member.id != 485513915548041239 else "48 hour special circumstances since I am usually active")

        if discord.utils.get(UFP.roles, id=954234917846388826) in member.roles:
            if (not str(member.id) in data):
                await remove_fleet_except(member, thirdFleet)
            elif (int(datetime.datetime.now().timestamp()) - data[str(member.id)] >= (30 * 86400)):
                await remove_fleet_except(member, thirdFleet)
            elif (30 * 86400) > int(datetime.datetime.now().timestamp()) - data[str(member.id)] >= (7 * 86400):
                await remove_fleet_except(member, secondFleet)
            elif (7 * 86400) > int(datetime.datetime.now().timestamp()) - data[str(member.id)] >= 0:
                await remove_fleet_except(member, firstFleet)
        else:
            await remove_fleet_except(member, None)

    chartData = jsonhandler.getActivity()

    if int(datetime.datetime.now().timestamp()) >= chartData["timestamp"] + 86400:
        UFP = await bot.fetch_guild(878364507385233480)
        total = 0
        active = 0
        reserve = 0
        commissioned = 0
        visitor = 0
        ambassador = 0
        roles = {
            "c": discord.utils.get(UFP.roles, id=954234917846388826),
            "r": discord.utils.get(UFP.roles, id=946227554136764416),
            "v": discord.utils.get(UFP.roles, id=954904188733767721),
            "a": discord.utils.get(UFP.roles, id=897176672825143296)
        }
        async for member in UFP.fetch_members(limit=1000):
            total += 1
            if roles["c"] in member.roles:
                if roles["r"] in member.roles:
                    reserve += 1
                else:
                    active += 1
                commissioned += 1
            elif roles["v"] in member.roles:
                if roles["a"] in member.roles:
                    ambassador += 1
                visitor += 1

        jsonhandler.setActivity(total, commissioned, active, reserve, visitor, ambassador, int(datetime.datetime.now().timestamp()))

@bot.command(name="warn", description="Warn a user with the rule broken included", guild_ids=[878364507385233480])
async def warnUser(ctx, member:discord.Member, messagelink, rulecitation):
    if ctx.author.id == 485513915548041239 or discord.utils.get(ctx.guild.roles, id=891514201569366087) in ctx.author.roles:
        await ranks.demoteMember(member, ctx.guild)
        numberOfWarns = warns.createWarn(member, rulecitation, messagelink, ctx.author)

        actionTaken = None
        if numberOfWarns == 1:
            actionTaken = "1 Day Timeout"
        elif numberOfWarns == 2:
            actionTaken = "1 Week Timeout"
        else:
            actionTaken = "1 Week Ban"

        embed = discord.Embed(
            title="Warning",
            color=0xff0000,
            description="Affected User: {}\n\nRule Cited: {}\nMessage Link: {}\nResponsible Senior Officer: {}\n\n-- ACTIONS TAKEN --\nDemotion, {}".format(member.mention, rulecitation, messagelink, ctx.author.mention, actionTaken)
        )

        secureChannel = await ctx.guild.fetch_channel(1091565333715898369)

        await secureChannel.send(embed=embed)
        await member.send(embed=embed)

        if numberOfWarns == 1:
            await member.timeout_for(datetime.timedelta(days=1))
        elif numberOfWarns == 2:
            await member.timeout_for(datetime.timedelta(days=7))
        else:
            await member.ban(reason="1 Week Ban for reaching 3 warnings")

        await ctx.respond("Done.")

@bot.command(name="warns", description="Check warns of a user", guild_ids=[878364507385233480])
async def checkwarns(ctx, member:discord.Member):
    if warns.getWarns(member):
        embed = discord.Embed(
            title="Warnings for {}".format(member),
            description="\n\n".join(["Rule Cited: {}\nMessage Link: {}\nResponsible Senior Officer: {}".format(warn["ruleCitation"], warn["messageLink"], warn["seniorOfficer"]) for warn in warns.getWarns(member)])
        )

        await ctx.respond(embed=embed)
    else:
        await ctx.respond("No warns found")

@bot.command(name="clearwarns", description="Clear warns of a user (LEAVE BLANK TO CLEAR ALL WARNS)", guild_ids=[878364507385233480])
async def clearwarns(ctx, member:discord.Member=None):
    if ctx.author.id == 485513915548041239 or discord.utils.get(ctx.guild.roles, id=891514201569366087) in ctx.author.roles:
        warns.deleteWarns(member)
        await ctx.respond("Done")

@bot.command(name="recognize", guild_ids=[878364507385233480])
async def recognizeFaction(ctx, faction):
    await ctx.defer()
    with open("json/factions.json", "r") as f:
        data = json.load(f)

    if faction in data["factions"]:
        await ctx.respond("Faction already recognized")

    data["factions"].append(faction)

    with open("json/factions.json", "w") as f:
        json.dump(data, f, indent = 4)

    channel = await ctx.guild.fetch_channel(907062178346065960)
    await channel.send("Now recognizing {} for affiliates".format(faction))
    await ctx.respond("Now recognizing {} for affiliates".format(faction))

async def getFactions(ctx):
    with open("json/factions.json", "r") as f:
        data = json.load(f)
    return [faction for faction in data["factions"] if faction.startswith(ctx.value)]

@bot.command(name="affiliate", description="Affiliate with a faction", guild_ids=[878364507385233480])
@discord.commands.option("faction", description="CASE SENSITIVE", autocomplete=getFactions)
async def affiliateFaction(ctx, faction, member: discord.Member=None):
    await ctx.defer()
    if member and not (discord.utils.get(ctx.guild.roles, id=891514201569366087) in ctx.author.roles):
        return await ctx.respond("You do not have permissions to use this parameter")
    member = member or ctx.author
    with open("json/factions.json", "r") as f:
        data = json.load(f)

    if not (faction in data["factions"]):
        return await ctx.respond("Faction not found (Check spelling and capitalization)")
    
    with open("json/affiliations.json", "r") as f:
        data = json.load(f)

    if not (str(member.id) in data):
        data[str(member.id)] = []

    if not (faction in data[str(member.id)]):
        data[str(member.id)].append(faction)
    
    with open("json/affiliations.json", "w") as f:
        json.dump(data, f, indent=4)
    
    await ctx.respond("Affiliations updated")

@bot.command(name="affiliations", description="View your faction affiliations", guild_ids=[878364507385233480])
async def affiliations(ctx, member: discord.Member=None):
    member = member or ctx.author
    await ctx.defer()

    with open("json/affiliations.json") as f:
        data = json.load(f)
    
    if not (str(member.id) in data):
        data[str(member.id)] = []

    embed = discord.Embed(
        title="Affiliations",
        color=0x0055ff,
        description="\n".join([faction for faction in data[str(member.id)]])
    )

    await ctx.respond(embed=embed)

@bot.command(name="restrict-affiliates", description="Restrict officers that are affiliated with a faction", guild_ids=[878364507385233480])
@discord.commands.option("faction", description="CASE SENSITIVE", autocomplete=getFactions)
async def restrictAffiliates(ctx, faction):
    await ctx.defer()
    with open("json/factions.json", "r") as f:
        data = json.load(f)

    if not (faction in data["factions"]):
        return await ctx.respond("Faction not found (Check spelling and capitalization)")
    
    restricted = discord.utils.get(ctx.guild.roles, id=1122368049157255180)
    commissioned = discord.utils.get(ctx.guild.roles, id=954234917846388826)

    with open("json/affiliations.json") as f:
        data = json.load(f)

    for member in ctx.guild.members:
        roles = member.roles
        if str(member.id) in data and faction in data[str(member.id)]:
            if commissioned in roles:
                if not (restricted in roles):
                    await member.add_roles(restricted)

                await member.remove_roles(commissioned)

    await ctx.respond("Restricted anyone affiliated with this faction")

@bot.command(name="unrestrict-affiliates", description="Restrict officers that are affiliated with a faction", guild_ids=[878364507385233480])
@discord.commands.option("faction", description="CASE SENSITIVE", autocomplete=getFactions)
async def unrestrictAffiliates(ctx, faction):
    await ctx.defer()
    with open("json/factions.json", "r") as f:
        data = json.load(f)

    if not (faction in data["factions"]):
        return await ctx.respond("Faction not found (Check spelling and capitalization)")
    
    restricted = discord.utils.get(ctx.guild.roles, id=1122368049157255180)
    commissioned = discord.utils.get(ctx.guild.roles, id=954234917846388826)

    with open("json/affiliations.json") as f:
        data = json.load(f)

    for member in ctx.guild.members:
        roles = member.roles
        if str(member.id) in data and faction in data[str(member.id)]:
            if restricted in roles:
                await member.remove_roles(restricted)
            
                if not (commissioned in roles):
                    await member.add_roles(commissioned)

    await ctx.respond("Unrestricted anyone affiliated with this faction")

@bot.event
async def on_ready():
    guild = await bot.fetch_guild(878364507385233480)
    channel = await guild.fetch_channel(1051489091339956235)
    embed = discord.Embed(title="Bot Status: Online", description="UFP Bot now connected to discord", color=0x0055ff)
    await channel.send("<@485513915548041239>", embed=embed)

    reserveTask.start()
    EventReminder.start()
    PointChecker.start()
    #channel = await guild.fetch_channel(878449851833151488)
    #msg = await channel.fetch_message(1118363480316182669)
    #await msg.edit("Little update on the moderation policy here today:\n\n- Transphobic stuff will lead to an automatic court martial\n\nThis change is because acfc is slowly gaining up on our asses mainly because they are getting curious and seeing the type of shit thats posted here ~~and cuz moderation wont do shit~~\n\n`- Admiral bungochungo`\n||<@&954234917846388826>||")

@bot.event
async def on_message(message):    
    if message.guild:
        offDuty = []
        for member in offduty.getUsers():
            offDuty.append(await message.guild.fetch_member(int(member)))

        reserve = discord.utils.get(message.guild.roles, id=946227554136764416)

        jsonhandler.setLastMesage(message.author)
        if reserve in message.author.roles:
            await message.author.remove_roles(reserve)

        if message.author in offDuty:
            offdutyInfo = offduty.getData(message.author.id)

            if offdutyInfo["autoText"]:
                await message.reply("Welcome back.")
                offduty.removeUser(message.author.id)
        else:
            for mention in message.mentions:
                if mention in offDuty:
                    offdutyInfo = offduty.getData(mention.id)
                    if ((mention.status == discord.Status.offline or mention.status == discord.Status.idle) if not offdutyInfo["autoText"] else True):
                        if not bot.mentioned:
                            bot.mentioned = True

                            await message.reply("The user that you have just tried to ping is logged as off-duty.\n\nThey are logged as `{}`\nThey are expected to return <t:{}:R>\n\n{}".format(offdutyInfo["eventType"], offdutyInfo["estimatedEnd"], "Message from the user: ```{}```".format(offdutyInfo["message"]) if offdutyInfo["message"] else ""), delete_after=3)
                            break

    flagPunishments = {
        "sexual": 5
    }

    punishments = []
    
    moderationMessage = client.moderations.create(
        input=message.content
    )

    moderationResults = moderationMessage.results[0]

    if moderationResults.flagged and not message.author.bot:
        for flag, value in moderationResults.categories.model_dump().items():
            if value and (flag in flagPunishments.keys()):
                punishments.append(flagPunishments[flag])

        if punishments:
            if discord.utils.get(message.guild.roles, id=891514201569366087) in message.author.roles:
                return await message.reply("ay bro bro set an example")
            offenseData = jsonhandler.getProgression(message.author)
            offenseNumber = jsonhandler.addProgression(message.author)

            if offenseNumber == 1:
                suffix = "st"
                timeout = 5
            elif offenseNumber == 2:
                suffix = "nd"
                timeout = 20
            elif offenseNumber == 3:
                suffix = "rd"
                timeout = 60

            if sum(punishments) == 5:
                embed = discord.Embed(
                    title="Flagged Message",
                    description="Your message has been flagged as being against the rules\n\n-- Scores: --\n{}".format(
                        "\n".join(["{} score: {}".format(flag.capitalize(), str(int(score * 100) / 100)) for flag, score in moderationResults.category_scores.model_dump().items() if moderationResults.categories.model_dump()[flag] and (flag in flagPunishments.keys())])
                    )
                )
                await message.reply(embed=embed)
            else:
                embed = discord.Embed(
                    title="Flagged Message",
                    description="Your message has been flagged as being against the rules\n\n-- Scores: --\n{}".format(
                        "\n".join(["{} score: {}".format(flag.capitalize(), str(int(score * 100) / 100)) for flag, score in moderationResults.category_scores.model_dump().items() if moderationResults.categories.model_dump()[flag] and (flag in flagPunishments.keys())])
                    )
                )
                await message.reply(embed=embed)
            await message.delete()
            UFP = await bot.fetch_guild(878364507385233480)
            channel = await UFP.fetch_channel(1051489091339956235)

            await channel.send("{}: {}".format(message.author, message.content))
"""
    detection = translator.detect(message.content)
    if detection.lang != "en" and message.author != bot.user and translator.translate(message.content, dest="en").text != message.content:
        await message.reply("Translation (`{}` {}% Confidence): {}".format(detection.lang, int(detection.confidence * 100), translator.translate(message.content, dest="en").text))
"""


@bot.event
async def on_message_edit(before, after):    
    message = after
    
    flagPunishments = {
        "sexual": 5
    }

    punishments = []

    moderationMessage = client.moderations.create(
        input=message.content
    )

    moderationResults = moderationMessage.results[0]

    if moderationResults.flagged and not message.author.bot:
        for flag, value in moderationResults.categories.model_dump().items():
            if value and (flag in flagPunishments.keys()):
                punishments.append(flagPunishments[flag])

        if punishments:
            if discord.utils.get(message.guild.roles, id=891514201569366087) in message.author.roles:
                return await message.reply("ay bro bro set an example")
            offenseData = jsonhandler.getProgression(message.author)
            offenseNumber = jsonhandler.addProgression(message.author)

            if offenseNumber == 1:
                suffix = "st"
                timeout = 5
            elif offenseNumber == 2:
                suffix = "nd"
                timeout = 20
            elif offenseNumber == 3:
                suffix = "rd"
                timeout = 60

            if sum(punishments) == 5:
                embed = discord.Embed(
                    title="Flagged Message",
                    description="Your message has been flagged as being against the rules\n\n-- Scores: --\n{}".format(
                        "\n".join(["{} score: {}".format(flag.capitalize(), str(int(score * 100) / 100)) for flag, score in moderationResults.category_scores.model_dump().items() if moderationResults.categories.model_dump()[flag] and (flag in flagPunishments.keys())])
                    )
                )
                await message.reply(embed=embed)
            else:
                embed = discord.Embed(
                    title="Flagged Message",
                    description="Your message has been flagged as being against the rules\n\n-- Scores: --\n{}".format(
                        "\n".join(["{} score: {}".format(flag.capitalize(), str(int(score * 100) / 100)) for flag, score in moderationResults.category_scores.model_dump().items() if moderationResults.categories.model_dump()[flag] and (flag in flagPunishments.keys())])
                    )
                )
                await message.reply(embed=embed)
            await message.delete()
            UFP = await bot.fetch_guild(878364507385233480)
            channel = await UFP.fetch_channel(1051489091339956235)

            await channel.send("{}: {}".format(message.author, message.content))

@bot.event
async def on_interaction(Interaction: discord.Interaction):
    if Interaction.is_component():
        try:
            await Interaction.response.defer()
        except:
            pass

        try:
            ParsedID = Interaction.custom_id.split(" | ")

            if len(ParsedID) != 2:
                return
            
            Action = ParsedID[0]
            LogID = ParsedID[1]
            
            if Action in ["Approve", "Edit", "Void"]:
                if not Interaction.user.get_role(1012070243004321802):
                    return await Interaction.respond(content="You aren't a Senior Officer", ephemeral=True)
                
                Pointlog = pointlog.Pointlog.FromID(Interaction, LogID)
                if not Pointlog:
                    return await Interaction.respond(content="Pointlog no longer exists.", ephemeral=True)

                if Action == "Approve":
                    await Pointlog.Approve(Interaction.channel)
                elif Action == "Edit":
                    await Interaction.respond(content="Begin stating your edits.\n\nCommands:\n    removeuser: <userid or mention>\n    removepoint: <point amount>\n    addmany: <point amount> - <users>", ephemeral=True)
                    
                    EditSuccess = False

                    while not EditSuccess:
                        EditSuccess = await Pointlog.EditPointlogDialog(bot, Interaction)

                        Pointlog.UpdateEmbed()

                        await Interaction.edit_original_message(embed=Pointlog.Embed)

                    Pointlog.Log()
                    await Interaction.respond(content="Successfully edited.", ephemeral=True)
                elif Action == "Void":
                    await Pointlog.Delete(Interaction.channel)
            elif Action in ["Promote", "Minimum", "Demote"]:
                if not Interaction.user.get_role(1012070243004321802):
                    return await Interaction.respond(content="You aren't a Senior Officer", ephemeral=True)
                
                Member = Interaction.guild.get_member(int(LogID))

                UserData = points.GetUser(LogID)

                if Action == "Promote":
                    await ranks.ReplaceRank(Member, Interaction.guild, int(ranks.GetMinimumRank(UserData["Points"])))
                elif Action == "Minimum":
                    UserData["Points"] = ranks.requirements[str(ranks.getRank(Member).id)]
                elif Action == "Demote":
                    await ranks.ReplaceRank(Member, Interaction.guild, int(ranks.GetMinimumRank(UserData["Points"])))

                UserData["WaitingForRankChange"] = False
                points.WriteKey(LogID, UserData)

                await Interaction.delete_original_message()
            elif Action in ["View Event"]:
                Event = eventhandler.GetEvent(LogID)
                if not Event:
                    return await Interaction.respond("Event not found.", ephemeral=True)

                OriginalMessage = await Interaction.original_message()

                if not Interaction.user.id in Event["Viewed"]:
                    MRChat = Interaction.guild.get_channel(1264678923145580544)
                    await MRChat.send("{} has viewed the event: {}".format(Interaction.user, OriginalMessage.jump_url))
                    eventhandler.AddViewed(LogID, Interaction.user.id)

                await Interaction.respond(embed=CreateEventEmbed(Interaction.guild, Event["EventType"], Event["EventTimestamp"], Interaction.guild.get_member(Event["EventHost"]), Event["EventNotes"], Event["EventDuration"], LogID), ephemeral=True)
            
        except Exception as e:
            error = discord.utils.get(Interaction.guild.channels, id=1051489091339956235)
            await error.send(traceback.format_exc())
    else:
        await bot.process_application_commands(Interaction)

Thread(target=webserver.run).start()
Thread(target=mentionedTask).start()
bot.run(getConfig("token"))