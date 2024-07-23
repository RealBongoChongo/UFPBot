import discord, random, typing, json, datetime
from copy import deepcopy
from . import points

characters = "a b c d e f g h i j k l m n o p q r s t u v w x y z 1 2 3 4 5 6 7 8 9 0".split()

def GenerateID() -> str:
    GeneratedID = []

    for i in range(6):
        IDChunk = ""
        for i in range(6):
            IDChunk += random.choice(characters)

        GeneratedID.append(IDChunk)

    return "-".join(GeneratedID)

def ReadJson() -> dict:
    return json.load(open("json/pointlogs.json", "r"))

def WriteJson(Data) -> None:
    json.dump(Data, open("json/pointlogs.json", "w"), indent=4)

def WriteKey(Key: str, Value) -> None:
    Data = ReadJson()

    Data[Key] = Value

    WriteJson(Data)

def GetPointlog(PointlogID: str) -> dict:
    if not PointlogID in ReadJson():
        return None
    
    return ReadJson()[PointlogID]

class PointlogButton(discord.ui.Button):
    def __init__(self, Label: str, PointlogID: str):
        Colors = {
            "Approve": discord.ButtonStyle.success,
            "Edit": discord.ButtonStyle.blurple,
            "Void": discord.ButtonStyle.danger,
        }

        super().__init__(label=Label, custom_id="{} | {}".format(Label, PointlogID), style=Colors[Label])

class Pointlog:
    def __init__(self, ctx: discord.ApplicationContext):
        self.Pointlog: dict = {}
        self.Logger: int = None
        self.Key: str = None
        self.Message: int = None

        self.Embed: discord.Embed = discord.Embed(
            color=0x0452cf
        )
        self.Embed.set_author(name="United Federation of Planets Pointlog", icon_url=ctx.guild.icon.url)

    def Log(self, Logger: int = None, MessageID: int = None) -> None:
        Key = self.Key or GenerateID()

        self.Key = Key
        self.Logger = self.Logger or Logger

        WriteKey(self.Key, {
            "Log": self.Pointlog,
            "Logger": self.Logger,
            "Message": self.Message or MessageID
        })

        self.Embed.set_footer(text="Pointlog ID: {}".format(self.Key))
        self.Embed.timestamp = datetime.datetime.now()

    def UpdateEmbed(self):
        self.Embed.clear_fields()

        for Point, Users in deepcopy(self.Pointlog).items():
            if not Users:
                continue

            self.Embed.add_field(name="{} Point{}".format(Point, "" if Point == 1 or Point == -1 else "s"), value=", ".join(["<@{}>".format(User) for User in Users]), inline=False)

    @classmethod
    def FromID(cls, ctx: discord.Interaction, PointlogID: str):
        self = cls.__new__(cls)

        Pointlog = GetPointlog(PointlogID)

        if not Pointlog:
            return

        self.Pointlog = Pointlog["Log"]
        self.Logger = Pointlog["Logger"]
        self.Message = Pointlog["Message"]
        self.Key = PointlogID

        self.Embed = discord.Embed(
            color=0x0452cf
        )
        self.Embed.set_author(name="United Federation of Planets Pointlog", icon_url=ctx.guild.icon.url)
        self.Embed.set_footer(text="Pointlog ID: {}".format(self.Key))
        self.Embed.timestamp = datetime.datetime.now()


        return self

    def ProcessUsers(self, Selector: str) -> list[int]:
        Users = Selector.split(", ")
        FinalUsers = []

        for User in Users:
            UserID = User.replace("<@", "").replace(">", "")

            try:
                UserID = int(UserID)
            except:
                continue

            FinalUsers.append(UserID)

        return FinalUsers
    
    def FindUserInPointlog(self, UserID: int, Delete: bool=False) -> int:
        for Point, Users in deepcopy(self.Pointlog).items():
            if UserID in Users:
                self.Pointlog[Point].remove(UserID)

                return int(Point)
            
        return 0
    
    def PointlogFromMessage(self, Message: str, Guild: discord.Guild, Overwrite: bool) -> None:
        if Overwrite:
            self.Pointlog = {}

        MessageLines = Message.split("\n")

        for Line in MessageLines:
            ParsedLine = Line.split(" - ")
            if len(ParsedLine) != 2:
                continue

            try:
                Point = int(ParsedLine[0])
            except:
                continue

            Users = ParsedLine[1].split(", ")

            for User in Users:
                UserID = User.replace("<@", "").replace(">", "")
                try:
                    int(UserID)
                except:
                    Member = Guild.get_member_named(UserID)
                    if Member:
                        UserID = Member.id
                    else:
                        continue

                Point = self.FindUserInPointlog(int(UserID), True) + Point
                    
                if not str(Point) in self.Pointlog:
                    self.Pointlog[str(Point)] = []

                self.Pointlog[str(Point)].append(int(UserID))

    def ToView(self) -> discord.ui.View:
        View = discord.ui.View()

        View.add_item(PointlogButton("Approve", self.Key))
        View.add_item(PointlogButton("Edit", self.Key))
        View.add_item(PointlogButton("Void", self.Key))

        return View

    async def Delete(self, Channel: discord.TextChannel) -> None:
        Message = await Channel.fetch_message(self.Message)
        await Message.delete()

        Data = ReadJson()
        Data.pop(self.Key)

        WriteJson(Data)

    async def Approve(self, Channel: discord.TextChannel) -> None:
        Message = await Channel.fetch_message(self.Message)
        await Message.delete()

        for Point, Users in deepcopy(self.Pointlog).items():
            Point = int(Point)

            for User in Users:
                points.AddPoints(User, Point)

        Data = ReadJson()
        Data.pop(self.Key)

        WriteJson(Data)

    async def CreatePointlogDialog(self, bot: discord.Bot, ctx: discord.ApplicationContext) -> bool:
        PointlogMessage = await bot.wait_for("message", check=lambda message: message.author == ctx.author and message.channel == ctx.channel and message.guild == ctx.guild)

        if PointlogMessage.content.lower() == "done":
            return True

        self.PointlogFromMessage(PointlogMessage.content, ctx.guild)

        return False
    
    async def EditPointlogDialog(self, Bot: discord.Bot, Interaction: discord.Interaction) -> bool:
        PointlogMessage = await Bot.wait_for("message", check=lambda message: message.author == Interaction.user and message.channel == Interaction.channel and message.guild == Interaction.guild)
        await PointlogMessage.delete()

        if PointlogMessage.content.lower() == "done":
            return True
        
        Actions = ["removeuser", "removepoint", "addmany"]

        ParsedAction = PointlogMessage.content.split(": ")

        if len(ParsedAction) != 2:
            return False
        
        Action = ParsedAction[0].lower()
        Argument = ParsedAction[1]

        if not Action in Actions:
            return False
        
        if Action == "removeuser":
            UserList = self.ProcessUsers(Argument)

            for User in UserList:
                for Point, Users in self.Pointlog.items():
                    if not User in Users:
                        continue

                    Users.remove(User)
        elif Action == "addmany":
            self.PointlogFromMessage(Argument, Interaction.guild)
        elif Action == "removepoint":
            self.Pointlog.pop(Argument)

        return False
    
class PointlogModal(discord.ui.Modal):
    def __init__(self, Log: Pointlog, Overwrite: bool):
        super().__init__(title="Pointlog Input", timeout=None)

        self.Pointlog: Pointlog = Log
        self.Overwrite: bool = Overwrite

        self.add_item(discord.ui.InputText(
            style=discord.InputTextStyle.multiline,
            placeholder="1 - amazangprizanor\n2 - sniperrifle57, 485513915548041239\n\n-1 - banmched, <@485513915548041239>",
            label="Discord IDs, Discord/Roblox Usernames"
        ))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        TextBox: discord.ui.InputText = self.children[0]

        self.Pointlog.PointlogFromMessage(TextBox.value, interaction.guild, self.Overwrite)
        self.Pointlog.UpdateEmbed()
        
        await interaction.edit_original_response(embed=self.Pointlog.Embed)

        return await super().callback(interaction)
    
class PointlogView(discord.ui.View):
    def __init__(self, Log: Pointlog):
        super().__init__(timeout=None)

        self.Pointlog: Pointlog = Log
        self.Cancelled: bool = False

    @discord.ui.button(label="Add Data", style=discord.ButtonStyle.gray)
    async def AddData(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(PointlogModal(self.Pointlog, False))

    @discord.ui.button(label="Overwrite Data", style=discord.ButtonStyle.gray)
    async def OverwriteData(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(PointlogModal(self.Pointlog, True))

    @discord.ui.button(label="Cancel Log", style=discord.ButtonStyle.danger, row=1)
    async def CancelLog(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.Cancelled = True

        self.stop()
        await interaction.delete_original_response()

    @discord.ui.button(label="Submit Log", style=discord.ButtonStyle.success, row=1)
    async def SubmitLog(self, button: discord.ui.Button, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True

        await interaction.edit_original_response(view=self)
        self.stop()