import discord
import json
from . import offduty

async def updateCommandingOfficers(bot, guild):
    with open("json/commandingOfficersCache.json", "r") as f:
        data = json.load(f)

    channel = await guild.fetch_channel(1173276222357262467)

    memberData = {
        "pres": None,
        "vpres": None,
        "chiefad": None,
        "chieftact": None,
        "chiefeng": None,
        "chiefsci": None,
        "chieflog": None,

        "ffleet": None,
        "sfleet": None,
        "tfleet": None,
    }

    offDuty = []
    for member in offduty.getUsers():
        offDuty.append(await guild.fetch_member(int(member)))
    
    async for member in guild.fetch_members(limit=1000):
        if discord.utils.get(guild.roles, id=953784681629900840) in member.roles:
            memberData["pres"] = member.mention + ("[OFF-DUTY]" if member in offDuty else "")
        if discord.utils.get(guild.roles, id=953784879189983252) in member.roles:
            memberData["vpres"] = member.mention + ("[OFF-DUTY]" if member in offDuty else "")
        if discord.utils.get(guild.roles, id=897176185941934140) in member.roles:
            memberData["chiefad"] = member.mention + ("[OFF-DUTY]" if member in offDuty else "")
        if discord.utils.get(guild.roles, id=1173087151081132133) in member.roles:
            memberData["chieftact"] = member.mention + ("[OFF-DUTY]" if member in offDuty else "")
        if discord.utils.get(guild.roles, id=891348779096240138) in member.roles:
            memberData["chiefeng"] = member.mention + ("[OFF-DUTY]" if member in offDuty else "")
        if discord.utils.get(guild.roles, id=948799489131552778) in member.roles:
            memberData["chiefsci"] = member.mention + ("[OFF-DUTY]" if member in offDuty else "")
        if discord.utils.get(guild.roles, id=1071043055651651594) in member.roles:
            memberData["chieflog"] = member.mention + ("[OFF-DUTY]" if member in offDuty else "")
        if discord.utils.get(guild.roles, id=958103453614354512) in member.roles:
            memberData["ffleet"] = member.mention + ("[OFF-DUTY]" if member in offDuty else "")
        if discord.utils.get(guild.roles, id=958103663451176981) in member.roles:
            memberData["sfleet"] = member.mention + ("[OFF-DUTY]" if member in offDuty else "")
        if discord.utils.get(guild.roles, id=958103804316880916) in member.roles:
            memberData["tfleet"] = member.mention + ("[OFF-DUTY]" if member in offDuty else "")

    embed = discord.Embed(
        title="Chain of Command",
        description="""
Federation President: {}
Federation Vice President: {}
Chief Admiral of Starfleet: {}

Chief Tactical Officer: {}
Chief Engineering Officer: {}
Chief Science Officer: {}
Chief Logistics Officer: {}

Secretary: <@485513915548041239>

First Fleet Commanding Officer: {}
Second Fleet Commanding Officer: {}
Third Fleet Commanding Officer: {}
        """.format(memberData["pres"], memberData["vpres"], memberData["chiefad"], memberData["chieftact"], memberData["chiefeng"], memberData["chiefsci"], memberData["chieflog"], memberData["ffleet"], memberData["sfleet"], memberData["tfleet"]),
    ).set_footer(text="Seniority is in the order as listed")

    msg = await channel.fetch_message(data["message"])

    if msg:
        await msg.edit(embed=embed)
    else:
        msg = await channel.send(embed=embed)

        with open("json/commandingOfficersCache.json", "w") as f:
            json.dump({"message": msg.id}, f, indent=4)