import discord
from discord.ext import tasks

from copy import deepcopy

from utility import pointlog, points, ranks

class Ranking(discord.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @tasks.loop(minutes=10)
    async def PointChecker(self):
        UFP = self.bot.get_guild(878364507385233480)
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

    @discord.command(name="my-points", description="Find your points", guild_ids=[878364507385233480])
    async def MyPoints(self, ctx: discord.ApplicationContext):
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

    @discord.command(name="get-points", description="Find someone else's points", guild_ids=[878364507385233480])
    async def GetPoints(self, ctx: discord.ApplicationContext, member: discord.Member):
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

    @discord.command(name="my-logs", description="View the IDs of the logs that you've sent in", guild_ids=[878364507385233480])
    async def ViewMyLogs(self, ctx: discord.ApplicationContext):
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

    @discord.command(name="all-logs", description="View the IDs of the logs that are pending", guild_ids=[878364507385233480])
    async def ViewPendingLogs(self, ctx: discord.ApplicationContext):
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

    @discord.command(name="view-log", description="View a pointlog", guild_ids=[878364507385233480])
    async def ViewLog(self, ctx: discord.ApplicationContext, logid: str):
        Pointlog = pointlog.Pointlog.FromID(logid)
        if not Pointlog:
            return await ctx.respond("Log does not exist")

        Pointlog.UpdateEmbed()

        await ctx.respond(embed=Pointlog.Embed)

    @discord.command(name="ranklock", description="Ranklock someone", guild_ids=[878364507385233480])
    async def RanklockUser(self, ctx: discord.ApplicationContext, member: discord.Member, setting: bool):
        UserData = points.GetUser(member.id)

        UserData["Ranklocked"] = setting

        points.WriteKey(member.id, UserData)

        await ctx.respond("User ranklocked.")

    @discord.command(name="view-consensus", description="View someone's consensus", guild_ids=[878364507385233480])
    async def ViewConsensus(self, ctx: discord.ApplicationContext, member: discord.Member):
        UserData = points.GetUser(member.id)

        if not UserData["Consensus"]:
            return await ctx.respond("User's consensus is empty")

        Embed = discord.Embed(
            description="\n".join(["{}: `{}` - <@{}>".format(UserData["Consensus"].index(Note), Note["Note"], Note["Creator"]) for Note in UserData["Consensus"]]),
            color=0x0452cf
        )
        Embed.set_author(name="United Federation of Planets", icon_url=ctx.guild.icon.url)

        await ctx.respond(embed=Embed)

    @discord.command(name="add-consensus", description="Add to someone's consensus", guild_ids=[878364507385233480])
    async def AddConsensus(self, ctx: discord.ApplicationContext, member: discord.Member, note: str):
        UserData = points.GetUser(member.id)

        UserData["Consensus"].append({
            "Note": note,
            "Creator": str(ctx.author.id)
        })

        points.WriteKey(member.id, UserData)

        await ctx.respond("Added to consensus.")

    @discord.command(name="remove-consensus", description="Remove an item from someone's consensus", guild_ids=[878364507385233480])
    async def RemoveConsensus(self, ctx: discord.ApplicationContext, member: discord.Member, position: int):
        UserData = points.GetUser(member.id)

        Item = UserData["Consensus"][position]

        UserData["Consensus"].remove(Item)

        points.WriteKey(member.id, UserData)

        await ctx.respond("Removed item from consensus.")

    @discord.command(name="clear-consensus", description="Clear someone's consensus", guild_ids=[878364507385233480])
    async def ClearConsensus(self, ctx: discord.ApplicationContext, member: discord.Member):
        UserData = points.GetUser(member.id)

        UserData["Consensus"] = []

        points.WriteKey(member.id, UserData)

        await ctx.respond("Cleared consensus.")

    @discord.command(name="create-pointlog", description="Create a pointlog", guild_ids=[878364507385233480])
    async def CreatePointlog(self, ctx: discord.ApplicationContext):
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

def add_cog(bot: discord.Bot):
    bot.add_cog(Ranking(bot))