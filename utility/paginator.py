import discord

class Paginator(discord.ui.View):
    def __init__(self, entries, color, title, ctx):
        self.page = 0
        self.entries = entries
        self.color = color
        self.title = title
        self.ctx = ctx
        super().__init__()

    @discord.ui.button(label="<<", style=discord.ButtonStyle.green)
    async def flipfront(self, button: discord.ui.Button, interation: discord.Interaction):
        if interation.user.id != self.ctx.author.id:
            await interation.response.send_message("You cannot use this!", ephemeral=True)
            return
        self.page = 0
        embed = discord.Embed(
            title=self.title,
            color=self.color,
            description=self.entries[self.page]
            if type(self.entries[self.page]) != dict
            else self.entries[self.page]["content"],
        )

        if type(self.entries[self.page]) == dict:
            embed.set_image(url=self.entries[self.page]["image"])
        embed.set_footer(text="Page ({}/{})".format(self.page + 1, len(self.entries)))
        await interation.message.edit(view=self, embed=embed)  
    
    @discord.ui.button(label="<", style=discord.ButtonStyle.green)
    async def flipback(self, button: discord.ui.Button, interation: discord.Interaction):
        if interation.user.id != self.ctx.author.id:
            await interation.response.send_message("You cannot use this!", ephemeral=True)
            return
        if self.page == 0:
            return
        self.page -= 1
        embed = discord.Embed(
            title=self.title,
            color=self.color,
            description=self.entries[self.page]
            if type(self.entries[self.page]) != dict
            else self.entries[self.page]["content"],
        )

        if type(self.entries[self.page]) == dict:
            embed.set_image(url=self.entries[self.page]["image"])
        embed.set_footer(text="Page ({}/{})".format(self.page + 1, len(self.entries)))
        await interation.message.edit(view=self, embed=embed)    

    @discord.ui.button(label=">", style=discord.ButtonStyle.green)
    async def flipforward(self, button: discord.ui.Button, interation: discord.Interaction):
        if interation.user.id != self.ctx.author.id:
            await interation.response.send_message("You cannot use this!", ephemeral=True)
            return
        if self.page + 1 == len(self.entries):
            return
        self.page += 1
        embed = discord.Embed(
            title=self.title,
            color=self.color,
            description=self.entries[self.page]
            if type(self.entries[self.page]) != dict
            else self.entries[self.page]["content"],
        )

        if type(self.entries[self.page]) == dict:
            embed.set_image(url=self.entries[self.page]["image"])
        embed.set_footer(text="Page ({}/{})".format(self.page + 1, len(self.entries)))
        await interation.message.edit(view=self, embed=embed)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.green)
    async def fliplast(self, button: discord.ui.Button, interation: discord.Interaction):
        if interation.user.id != self.ctx.author.id:
            await interation.response.send_message("You cannot use this!", ephemeral=True)
            return
        self.page = len(self.entries) - 1
        embed = discord.Embed(
            title=self.title,
            color=self.color,
            description=self.entries[self.page]
            if type(self.entries[self.page]) != dict
            else self.entries[self.page]["content"],
        )

        if type(self.entries[self.page]) == dict:
            embed.set_image(url=self.entries[self.page]["image"])
        embed.set_footer(text="Page ({}/{})".format(self.page + 1, len(self.entries)))
        await interation.message.edit(view=self, embed=embed)  

class Pag:
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.color = kwargs.get("color")
        self.entries = kwargs.get("entries")
    
    async def start(self, ctx):
        embed = discord.Embed(
            title=self.title,
            color=self.color,
            description=self.entries[0]
            if type(self.entries[0]) != dict
            else self.entries[0]["content"],
        )

        if type(self.entries[0]) == dict:
            embed.set_image(url=self.entries[0]["image"])
        embed.set_footer(text="Page (1/{})".format(len(self.entries)))
        await ctx.send(embed=embed, view=Paginator(self.entries, self.color, self.title, ctx))