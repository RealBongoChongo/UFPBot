import discord
from . import jsonhandler

shop = [
    {
        "tier": 1,
        "name": "Guerilla Class Ship",
        "cost": 0
    },
    {
        "tier": 2,
        "name": "Constitution Class Ship",
        "cost": 50000
    }
]

class Interface(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)

        self.ctx = ctx

    @discord.ui.select(options=[discord.SelectOption(label=ship["name"]) for ship in shop])
    async def selectShip(self, select: discord.ui.Select, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("You cannot do this", ephemeral=True)

        data = jsonhandler.getAccount(self.ctx.author)

        if select.values[0] in data["ships"]:
            return await interaction.response.send_message("You already have this ship!", ephemeral=True)

        for item in shop:
            if item["name"] == select.values[0]:
                if data["latinum"]["bars"] < item["cost"]:
                    return await interaction.response.send_message("You do not have enough latinum for this!", ephemeral=True)

                jsonhandler.removeLatinum(self.ctx.author, "bars", item["cost"])
                jsonhandler.addShip(self.ctx.author, item)

                enums = {
                    "1": "Common",
                    "2": "Uncommon",
                    "3": "Rare",
                    "4": "Epic",
                    "5": "Legendary",
                    "6": "Mythic"
                }

                embed = discord.Embed(
                    title="Ship Shop",
                    description=""
                )

                for item in shop:
                    embed.description += '**[{}]** `{}` —— **{cost:,d}** Bars of Gold-Pressed Latinum\n- {tier}x All Stats\n\n'.format(enums[str(item["tier"])], item["name"], cost=item["cost"], tier=item["tier"])

                self.disable_all_items()

                await interaction.response.edit_message(embed=embed, view=self)
                await interaction.followup.send("Purchase successful")

class EquipSelector(discord.ui.Select):
    def __init__(self, ctx, ships):
        super().__init__(options=[discord.SelectOption(label=ship["name"]) for ship in ships])

        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("You cannot do this", ephemeral=True)

        data = jsonhandler.getAccount(self.ctx.author)

        if data["equipped"] == data["ships"][self.values[0]]:
            return await interaction.response.send_message("You have already equipped this ship", ephemeral=True)

        jsonhandler.setShipEqupped(self.ctx.author, data["ships"][self.values[0]])

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

        self.view.disable_all_items()

        await interaction.response.edit_message(embed=embed, view=self.view)
        await interaction.followup.send("Ship successfully equipped")


class EquipInterface(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)

        self.ctx = ctx

        data = jsonhandler.getAccount(self.ctx.author)

        self.add_item(EquipSelector(ctx, data["ships"].values()))

    