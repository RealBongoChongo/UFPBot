import discord, datetime

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