import discord
from . import jsonhandler

ranks = [
    878368140759797850, 
    914732053789040660,
    878367994009505833,
    914732221611515904,
    878367891559448589,
    878367800937304146,
    940456287496470578,
    1022239558093512825,
    940456210799411220,
    878367592706887761,
    940455959858413658
]

requirements = {
    "878368140759797850": 0, 
    "914732053789040660": 10,
    "878367994009505833": 25,
    "914732221611515904": 40,
    "878367891559448589": 75,
    "878367800937304146": 100,
    "940456287496470578": None,
    "1022239558093512825": None,
    "940456210799411220": None,
    "878367592706887761": None,
    "940455959858413658": None
}

medals = [
    924064486858588161,
    951249495121858581,
    951249622402207814,
    951245830935953480,
    951244874538156082,
    951246241705107496,
    951245930047352913,
    951255054147547166,
    951255111584329799,
    951246316091109428,
    1056353526286131261,
    1135985572226285750,
    970407128651161620,
    1097345709998612480
]

def getRank(member):
    roles = member.roles
    for role in roles:
        if role.id in ranks:
            return role

    return None

def GetMinimumRank(Points: int) -> int:
    LastRank = None

    for RoleID, Point in requirements.items():
        if not LastRank:
            LastRank = RoleID
            continue

        if not Point:
            continue

        if Point >= Points:
            return LastRank
        
        LastRank = RoleID
        
    return None

def GetRankAbove(member: discord.Member) -> int:
    roles = member.roles
    for role in roles:
        if role.id in ranks:
            rankIndex = ranks.index(role.id)
            newRank = ranks[rankIndex + 1 if rankIndex != (len(ranks) - 1) else 0]

            return newRank

def GetRankBelow(member: discord.Member) -> int:
    roles = member.roles
    for role in roles:
        if role.id in ranks:
            rankIndex = ranks.index(role.id)
            newRank = ranks[rankIndex - 1 if rankIndex != 0 else 0]

            return newRank

async def ReplaceRank(member: discord.Member, Guild: discord.Guild, Rank: int):
    await member.remove_roles(getRank(member))
    await member.add_roles(discord.utils.get(Guild.roles, id=Rank))

async def demoteMember(member, guild, OverrideRank: int = None):
    roles = member.roles
    for role in roles:
        if role.id in ranks:
            rankIndex = ranks.index(role.id)
            newRank = ranks[rankIndex - 1 if rankIndex != 0 else 0]

            await member.remove_roles(role)
            await member.add_roles(discord.utils.get(guild.roles, id=newRank))
            return

async def promoteMember(member, guild):
    roles = member.roles
    for role in roles:
        if role.id in ranks:
            rankIndex = ranks.index(role.id)
            newRank = ranks[rankIndex + 1 if rankIndex != (len(ranks) - 1) else 0]

            await member.remove_roles(role)
            await member.add_roles(discord.utils.get(guild.roles, id=newRank))
            return

def getAssignment(member):
    roles = member.roles

    for role in roles:
        if role.id in [953784681629900840, 953784879189983252, 897176185941934140]:
            return role

    for role in roles:
        if role.id in [958103453614354512, 958097146761084958, 958103663451176981, 958097259201957928, 958103804316880916, 958097325299990621]:
            return role

    for role in roles:
        if role.id in [897176672825143296]:
            return role

    return None

def getMedals(member):
    roles = member.roles
    medalsGotten = []
    for role in roles:
        if role.id in medals:
            medalsGotten.append(role)

    return None if not medalsGotten else medalsGotten