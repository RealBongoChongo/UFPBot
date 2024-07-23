import discord
from discord.ext import tasks

import datetime

from utility import eventhandler, embeds

class EventButton(discord.ui.Button):
    def __init__(self, Label: str, PointlogID: str):
        super().__init__(label=Label, custom_id="{} | {}".format(Label, PointlogID), style=discord.ButtonStyle.gray)

class Events(discord.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

        self.EventReminder.start()

    def cog_unload(self) -> None:
        self.EventReminder.stop()

        return super().cog_unload()

    @discord.command(name="create-event", description="Create a classified event for Commissioned Personnel (TIME MUST BE IN UTC)", guild_ids=[878364507385233480])
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

        events = await ctx.guild.fetch_channel(1263544155691286639)

        await msg.edit("Sending Event Embed Into <#{}>...".format(events.id))

        View = discord.ui.View()
        View.add_item(EventButton("View Event", EventID))

        await events.send("**A new event has been scheduled.**", view=View)

        await msg.edit("Successfully scheduled the event.")

    @discord.command(name="get-event", description="Retrive an event created", guild_ids=[878364507385233480])
    async def GetEvent(ctx: discord.ApplicationContext, eventid: str):
        Event = eventhandler.GetEvent(eventid)
        if not Event:
            return await ctx.respond("Event not found.")

        await ctx.respond(embed=embeds.CreateEventEmbed(ctx.guild, Event["EventType"], Event["EventTimestamp"], ctx.guild.get_member(Event["EventHost"]), Event["EventNotes"], Event["EventDuration"], eventid))

    @discord.command(name="edit-event", description="Retrive an event created", guild_ids=[878364507385233480])
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

    @discord.command(name="delete-event", description="Delete an event created", guild_ids=[878364507385233480])
    async def DeleteEvent(ctx: discord.ApplicationContext, eventid: str):
        Event = eventhandler.GetEvent(eventid)
        if not Event:
            return await ctx.respond("Event not found.")
        
        eventhandler.DeleteEvent(eventid)

        await ctx.respond("Deleted")

    @tasks.loop(minutes=1)
    async def EventReminder(self):
        UFP = self.bot.get_guild(878364507385233480)
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

                EventEmbed = embeds.CreateEventEmbed(UFP, EventData["EventType"], EventData["EventTimestamp"], UFP.get_member(EventData["EventHost"]), EventData["EventNotes"], EventData["EventDuration"], EventID)

                await EventChannel.send("<@&954234917846388826> **This event starts in less than an hour.**", embed=EventEmbed)

                eventhandler.EditEvent(EventID, EventData)

            if EventData["EventTimestamp"] < TimestampNow and not EventData["Announced"]:
                EventData["Announced"] = True

                EventEmbed = embeds.CreateEventEmbed(UFP, EventData["EventType"], EventData["EventTimestamp"], UFP.get_member(EventData["EventHost"]), EventData["EventNotes"], EventData["EventDuration"], EventID)

                await EventChannel.send("<@&954234917846388826> **This event has started.**", embed=EventEmbed)

                eventhandler.EditEvent(EventID, EventData)

def setup(bot: discord.Bot):
    bot.add_cog(Events(bot))