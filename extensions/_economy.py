import discord

import random

from utility import jsonhandler, blackjack, upgrades, ships

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

latinumTypes = ["Bars", "Strips", "Slips"]
latinumTypesLower = ["bars", "strips", "slips"]

async def getLatinumTypes(ctx):
    return [latinumType for latinumType in latinumTypes if latinumType.lower().startswith(ctx.value.lower())]

class Economy(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot: discord.Bot = bot

    @discord.command(name="balance", description="Check your amoung of latinum", guild_ids=[878364507385233480])
    async def balance(ctx, member:discord.Member=None):
        data = jsonhandler.getAccount(member or ctx.author)

        embed = discord.Embed(
            title="{}'s Balance".format(member or ctx.author),
            description="- Latinum:\n  - Bars: {val1:,}\n  - Strips: {val2:,}\n  - Slips: {val3:,}".format(val1=data["latinum"]["bars"], val2=data["latinum"]["strips"], val3=data["latinum"]["slips"])
        )

        await ctx.respond(embed=embed)

    @discord.command(name="exchange", description="Exchange your latinum for different pieces of latinum", guild_ids=[878364507385233480])
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

    @discord.command(name="share", description="Scam people or graciously give latinum to people", guild_ids=[878364507385233480])
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

    @discord.command(name="leaderboard", description="Find out who is the richest in latinum", guild_ids=[878364507385233480])
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

    @discord.command(name="slots", description="Win some latinum", guild_ids=[878364507385233480])
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

    @discord.command(name="snakeeyes", description="Win some latinum", guild_ids=[878364507385233480])
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

    @discord.command(name="blackjack", description="Win some latinum", guild_ids=[878364507385233480])
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

    @discord.command(name="free", description="Only works if you are broke", guild_ids=[878364507385233480])
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

    @discord.command(name="ship", description="Look at ur ship stats", guild_ids=[878364507385233480])
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

    @discord.command(name="repair", description="Repair your ship", guild_ids=[878364507385233480])
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

    @discord.command(name="autorepair", description="Setup auto-repair for after debris scrounging", guild_ids=[878364507385233480])
    async def autoRepair(ctx, setting:bool):
        data = jsonhandler.getAccount(ctx.author)
        jsonhandler.setSetting(ctx.author, setting)

        await ctx.respond("Successfully changed setting")

    @discord.command(name="debris", description="Scrounge through debris", guild_ids=[878364507385233480])
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