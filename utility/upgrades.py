from . import jsonhandler
import discord

shop = {
    "Shield Generators": [
        {
            "tier": "MK I",
            "cost": 0,
            "capacity": 500
        },
        {
            "tier": "MK II",
            "cost": 20000,
            "capacity": 750
        },
        {
            "tier": "MK III",
            "cost": 30000,
            "capacity": 1000
        },
        {
            "tier": "MK IV",
            "cost": 40000,
            "capacity": 1250
        },
        {
            "tier": "MK V",
            "cost": 50000,
            "capacity": 1500
        },
        {
            "tier": "MK VI",
            "cost": 100000,
            "capacity": 2000
        },
        {
            "tier": "MK VII",
            "cost": 150000,
            "capacity": 2500
        },
        {
            "tier": "MK VIII",
            "cost": 200000,
            "capacity": 3000
        },
        {
            "tier": "MK IX",
            "cost": 250000,
            "capacity": 3500
        },
        {
            "tier": "MK X",
            "cost": 300000,
            "capacity": 4000
        },
        {
            "tier": "MK XI",
            "cost": 400000,
            "capacity": 5000
        },
        {
            "tier": "MK XII",
            "cost": 500000,
            "capacity": 6000
        },
        {
            "tier": "MK XIII",
            "cost": 600000,
            "capacity": 7000
        },
        {
            "tier": "MK XIV",
            "cost": 700000,
            "capacity": 8000
        },
        {
            "tier": "MK XV",
            "cost": 800000,
            "capacity": 10000
        }
    ],
    "Structural Integrity Fields": [
        {
            "tier": "MK I",
            "cost": 0,
            "capacity": 500
        },
        {
            "tier": "MK II",
            "cost": 40000,
            "capacity": 750
        },
        {
            "tier": "MK III",
            "cost": 60000,
            "capacity": 1000
        },
        {
            "tier": "MK IV",
            "cost": 80000,
            "capacity": 1250
        },
        {
            "tier": "MK V",
            "cost": 100000,
            "capacity": 1500
        },
        {
            "tier": "MK VI",
            "cost": 200000,
            "capacity": 2000
        },
        {
            "tier": "MK VII",
            "cost": 300000,
            "capacity": 2500
        },
        {
            "tier": "MK VIII",
            "cost": 400000,
            "capacity": 3000
        },
        {
            "tier": "MK IX",
            "cost": 500000,
            "capacity": 3500
        },
        {
            "tier": "MK X",
            "cost": 600000,
            "capacity": 4000
        },
        {
            "tier": "MK XI",
            "cost": 800000,
            "capacity": 5000
        },
        {
            "tier": "MK XII",
            "cost": 1000000,
            "capacity": 6000
        },
        {
            "tier": "MK XIII",
            "cost": 1200000,
            "capacity": 7000
        },
        {
            "tier": "MK XIV",
            "cost": 1400000,
            "capacity": 8000
        },
        {
            "tier": "MK XV",
            "cost": 1600000,
            "capacity": 10000
        }
    ],
    "Phasers": [
        {
            "tier": "MK I",
            "cost": 0,
            "damage": 25
        },
        {
            "tier": "MK II",
            "cost": 20000,
            "damage": 50
        },
        {
            "tier": "MK III",
            "cost": 30000,
            "damage": 75
        },
        {
            "tier": "MK IV",
            "cost": 40000,
            "damage": 100
        },
        {
            "tier": "MK V",
            "cost": 50000,
            "damage": 150
        },
        {
            "tier": "MK VI",
            "cost": 100000,
            "damage": 200
        },
        {
            "tier": "MK VII",
            "cost": 150000,
            "damage": 250
        },
        {
            "tier": "MK VIII",
            "cost": 200000,
            "damage": 300
        },
        {
            "tier": "MK IX",
            "cost": 250000,
            "damage": 350
        },
        {
            "tier": "MK X",
            "cost": 300000,
            "damage": 400
        },
        {
            "tier": "MK XI",
            "cost": 400000,
            "damage": 500
        },
        {
            "tier": "MK XII",
            "cost": 500000,
            "damage": 600
        },
        {
            "tier": "MK XIII",
            "cost": 600000,
            "damage": 700
        },
        {
            "tier": "MK XIV",
            "cost": 700000,
            "damage": 800
        },
        {
            "tier": "MK XV",
            "cost": 800000,
            "damage": 1000
        }
    ],
    "Torpedo Launchers": [
        {
            "tier": "MK I",
            "cost": 0,
            "damage": 25
        },
        {
            "tier": "MK II",
            "cost": 40000,
            "damage": 50
        },
        {
            "tier": "MK III",
            "cost": 60000,
            "damage": 75
        },
        {
            "tier": "MK IV",
            "cost": 80000,
            "damage": 100
        },
        {
            "tier": "MK V",
            "cost": 100000,
            "damage": 150
        },
        {
            "tier": "MK VI",
            "cost": 200000,
            "damage": 200
        },
        {
            "tier": "MK VII",
            "cost": 300000,
            "damage": 250
        },
        {
            "tier": "MK VIII",
            "cost": 400000,
            "damage": 300
        },
        {
            "tier": "MK IX",
            "cost": 500000,
            "damage": 350
        },
        {
            "tier": "MK X",
            "cost": 600000,
            "damage": 400
        },
        {
            "tier": "MK XI",
            "cost": 800000,
            "damage": 500
        },
        {
            "tier": "MK XII",
            "cost": 1000000,
            "damage": 600
        },
        {
            "tier": "MK XIII",
            "cost": 1200000,
            "damage": 700
        },
        {
            "tier": "MK XIV",
            "cost": 1400000,
            "damage": 800
        },
        {
            "tier": "MK XV",
            "cost": 1600000,
            "damage": 1000
        }
    ],
    "Deuterium Tanks": [
        {
            "tier": "MK I",
            "cost": 0,
            "capacity": 100
        },
        {
            "tier": "MK II",
            "cost": 20000,
            "capacity": 125
        },
        {
            "tier": "MK III",
            "cost": 30000,
            "capacity": 150
        },
        {
            "tier": "MK IV",
            "cost": 40000,
            "capacity": 175
        },
        {
            "tier": "MK V",
            "cost": 50000,
            "capacity": 200
        },
        {
            "tier": "MK VI",
            "cost": 100000,
            "capacity": 250
        },
        {
            "tier": "MK VII",
            "cost": 150000,
            "capacity": 300
        },
        {
            "tier": "MK VIII",
            "cost": 200000,
            "capacity": 350
        },
        {
            "tier": "MK IX",
            "cost": 250000,
            "capacity": 400
        },
        {
            "tier": "MK X",
            "cost": 300000,
            "capacity": 450
        },
        {
            "tier": "MK XI",
            "cost": 400000,
            "capacity": 600
        },
        {
            "tier": "MK XII",
            "cost": 500000,
            "capacity": 700
        },
        {
            "tier": "MK XIII",
            "cost": 600000,
            "capacity": 900
        },
        {
            "tier": "MK XIV",
            "cost": 700000,
            "capacity": 1000
        },
        {
            "tier": "MK XV",
            "cost": 800000,
            "capacity": 1100
        }
    ]
}

class SelectMarks(discord.ui.Select):
    def __init__(self, ctx, category):
        super().__init__(options=[discord.SelectOption(label=item["tier"]) for item in shop[category]])

        self.ctx = ctx
        self.category = category

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("You cannot do this", ephemeral=True)
        data = jsonhandler.getAccount(self.ctx.author)

        for item in shop[self.category]:
            if item["tier"] == self.values[0]:
                if item in data["equipment"][self.category]:
                    return await interaction.response.send_message("You already have this equipment!", ephemeral=True)

                if data["latinum"]["bars"] < item["cost"]:
                    return await interaction.response.send_message("You do not have enough latinum for this!", ephemeral=True)

                jsonhandler.removeLatinum(self.ctx.author, "bars", item["cost"])
                jsonhandler.addEquipment(self.ctx.author, self.category, item)

                embed = discord.Embed(
                    title="Ship Equipment Shop",
                    description=""
                )

                for item in shop[self.category]:
                    embed.description += '**[{}]** `{}` —— **{cost:,d}** Bars of Gold-Pressed Latinum\n{thing1} - {thing2:,}\n\n'.format(item["tier"], self.category, cost=item["cost"], thing1="Capacity" if "capacity" in item else "Damage", thing2=item["capacity"] if "capacity" in item else item["damage"])

                await interaction.response.send_message("Purchase Successful", ephemeral=True)

class SelectCategories(discord.ui.Select):
    def __init__(self, ctx):
        super().__init__(options=[discord.SelectOption(label=category) for category in shop.keys()])

        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("You cannot do this", ephemeral=True)

        markSelect = SelectMarks(self.ctx, self.values[0])
        if len(self.view.children) == 2:
            self.view.remove_item(self.view.children[1])
        self.view.add_item(markSelect)

        embed = discord.Embed(
            title="Ship Equipment Shop",
            description=""
        )

        for item in shop[self.values[0]]:
            embed.description += '**[{}]** `{}` —— **{cost:,d}** Bars of Gold-Pressed Latinum\n{thing1} - {thing2:,}\n\n'.format(item["tier"], self.values[0], cost=item["cost"], thing1="Capacity" if "capacity" in item else "Damage", thing2=item["capacity"] if "capacity" in item else item["damage"])

        await interaction.response.edit_message(embed=embed, view=self.view)


class Interface(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)

        self.ctx = ctx

        self.add_item(SelectCategories(ctx))

class EquipSelectMarks(discord.ui.Select):
    def __init__(self, ctx, category):
        data = jsonhandler.getAccount(ctx.author)

        super().__init__(options=[discord.SelectOption(label=item["tier"]) for item in data["equipment"][category]])

        self.ctx = ctx
        self.category = category

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("You cannot do this", ephemeral=True)
        data = jsonhandler.getAccount(self.ctx.author)

        table = {
            "Shield Generators": "sg",
            "Structural Integrity Fields": "sif",
            "Phasers": "p",
            "Torpedo Launchers": "tl",
            "Deuterium Tanks": "dt"
        }

        for item in shop[self.category]:
            if item["tier"] == self.values[0]:
                if data["equipped"]["equipment"][table[self.category]] == item:
                    return await interaction.response.send_message("You have already equipped this", ephemeral=True)

                jsonhandler.setEquipmentEqupped(self.ctx.author, table[self.category], item)

                embed = discord.Embed(
                    title="Ship Equipment Roster",
                    description=""
                )

                for item in data["equipment"][self.category]:
                    embed.description += '**[{}]** `{}`\n{thing1} - {thing2:,}\n\n'.format(item["tier"], self.category, thing1="Capacity" if "capacity" in item else "Damage", thing2=item["capacity"] if "capacity" in item else item["damage"])

                await interaction.response.send_message("Equip Successful", ephemeral=True)

class EquipSelectCategories(discord.ui.Select):
    def __init__(self, ctx):
        super().__init__(options=[discord.SelectOption(label=category) for category in shop.keys()])

        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("You cannot do this", ephemeral=True)

        data = jsonhandler.getAccount(self.ctx.author)

        markSelect = EquipSelectMarks(self.ctx, self.values[0])
        if len(self.view.children) == 2:
            self.view.remove_item(self.view.children[1])
        if data["equipment"][self.values[0]]:
            self.view.add_item(markSelect)

        embed = discord.Embed(
            title="Ship Equipment Roster",
            description=""
        )

        for item in data["equipment"][self.values[0]]:
            embed.description += '**[{}]** `{}`\n{thing1} - {thing2:,}\n\n'.format(item["tier"], self.values[0], thing1="Capacity" if "capacity" in item else "Damage", thing2=item["capacity"] if "capacity" in item else item["damage"])

        await interaction.response.edit_message(embed=embed, view=self.view)

class EquipInterface(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)

        self.ctx = ctx

        self.add_item(EquipSelectCategories(ctx))