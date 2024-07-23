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
    return json.load(open("json/smartlogs.json", "r"))

def WriteJson(Data) -> None:
    json.dump(Data, open("json/smartlogs.json", "w"), indent=4)

def WriteKey(Key: str, Value) -> None:
    Data = ReadJson()

    Data[Key] = Value

    WriteJson(Data)

def GetSmartlog(SmartlogID: str) -> dict:
    if not SmartlogID in ReadJson():
        return None
    
    return ReadJson()[SmartlogID]

class SmartlogButton(discord.ui.Button):
    def __init__(self, Label: str, SmartlogID: str):
        Colors = {
            "Approve": discord.ButtonStyle.success,
            "Edit": discord.ButtonStyle.blurple,
            "Void": discord.ButtonStyle.danger,
        }

        super().__init__(label=Label, custom_id="{} | {}".format(Label, SmartlogID), style=Colors[Label])

class Smartlog:
    def __init__(self, ctx: discord.ApplicationContext):
        self.Smartlog: dict = {}
        self.Logger: int = None
        self.Key: str = None
        self.Message: int = None

        self.Embed: discord.Embed = discord.Embed(
            color=0x0452cf
        )
        self.Embed.set_author(name="United Federation of Planets Smartlog", icon_url=ctx.guild.icon.url)

    def Log(self, Logger: int = None, MessageID: int = None) -> None:
        Key = self.Key or GenerateID()

        self.Key = Key
        self.Logger = self.Logger or Logger

        WriteKey(self.Key, {
            "Log": self.Smartlog,
            "Logger": self.Logger,
            "Message": self.Message or MessageID
        })

        self.Embed.set_footer(text="Smartlog ID: {}".format(self.Key))
        self.Embed.timestamp = datetime.datetime.now()

    def UpdateEmbed(self):
        self.Embed.clear_fields()

        for Point, Users in deepcopy(self.Smartlog).items():
            self.Embed.add_field(name="{} Point{}".format(Point, "" if Point == 1 or Point == -1 else "s"), value=", ".join(["<@{}>".format(User) for User in Users]), inline=False)

    @classmethod
    def FromID(cls, ctx: discord.Interaction, SmartlogID: str):
        self = cls.__new__(cls)

        Smartlog = GetSmartlog(SmartlogID)

        if not Smartlog:
            return

        self.Smartlog = Smartlog["Log"]
        self.Logger = Smartlog["Logger"]
        self.Message = Smartlog["Message"]
        self.Key = SmartlogID

        self.Embed = discord.Embed(
            color=0x0452cf
        )
        self.Embed.set_author(name="United Federation of Planets Smartlog", icon_url=ctx.guild.icon.url)
        self.Embed.set_footer(text="Smartlog ID: {}".format(self.Key))
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
    
    def FindUserInSmartlog(self, UserID: int, Delete: bool=False) -> int:
        for Point, Users in deepcopy(self.Smartlog).items():
            if UserID in Users:
                self.Smartlog[Point].remove(UserID)

                return int(Point)
            
        return 0
    
    def SmartlogFromMessage(self, Message: str, Guild: discord.Guild, Overwrite: bool) -> None:
        if Overwrite:
            self.Smartlog = {}

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

            if not str(Point) in self.Smartlog:
                self.Smartlog[str(Point)] = []

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
                
                Point = self.FindUserInSmartlog(int(UserID), True) + Point

                self.Smartlog[str(Point)].append(int(UserID))

    def ToView(self) -> discord.ui.View:
        View = discord.ui.View()

        View.add_item(SmartlogButton("Approve", self.Key))
        View.add_item(SmartlogButton("Edit", self.Key))
        View.add_item(SmartlogButton("Void", self.Key))

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

        for Point, Users in deepcopy(self.Smartlog).items():
            Point = int(Point)

            for User in Users:
                points.AddPoints(User, Point)

        Data = ReadJson()
        Data.pop(self.Key)

        WriteJson(Data)

    async def CreateSmartlogDialog(self, bot: discord.Bot, ctx: discord.ApplicationContext) -> bool:
        SmartlogMessage = await bot.wait_for("message", check=lambda message: message.author == ctx.author and message.channel == ctx.channel and message.guild == ctx.guild)

        if SmartlogMessage.content.lower() == "done":
            return True

        self.SmartlogFromMessage(SmartlogMessage.content, ctx.guild)

        return False
    
    async def EditSmartlogDialog(self, Bot: discord.Bot, Interaction: discord.Interaction) -> bool:
        SmartlogMessage = await Bot.wait_for("message", check=lambda message: message.author == Interaction.user and message.channel == Interaction.channel and message.guild == Interaction.guild)
        await SmartlogMessage.delete()

        if SmartlogMessage.content.lower() == "done":
            return True
        
        Actions = ["removeuser", "removepoint", "addmany"]

        ParsedAction = SmartlogMessage.content.split(": ")

        if len(ParsedAction) != 2:
            return False
        
        Action = ParsedAction[0].lower()
        Argument = ParsedAction[1]

        if not Action in Actions:
            return False
        
        if Action == "removeuser":
            UserList = self.ProcessUsers(Argument)

            for User in UserList:
                for Point, Users in self.Smartlog.items():
                    if not User in Users:
                        continue

                    Users.remove(User)
        elif Action == "addmany":
            self.SmartlogFromMessage(Argument, Interaction.guild)
        elif Action == "removepoint":
            self.Smartlog.pop(Argument)

        return False
    
class SmartlogModal(discord.ui.Modal):
    def __init__(self, Log: Smartlog, Overwrite: bool):
        super().__init__(title="Smartlog Input", timeout=None)

        self.Smartlog: Smartlog = Log
        self.Overwrite: bool = Overwrite

        self.add_item(discord.ui.InputText(
            style=discord.InputTextStyle.multiline,
            placeholder="1 - gogomangothacked2341, amazangprizanor, bungochungo\n2 - sniperrifle57, 485513915548041239\n\n-1 - banmched, <@485513915548041239>\n-2 - fatass",
            label="Discord IDs, Discord Usernames/Nicknames, Roblox Usernames, or raw pings"
        ))

    async def callback(self, interaction: discord.Interaction):
        TextBox: discord.ui.InputText = self.children[0]

        self.Smartlog.SmartlogFromMessage(TextBox.value, interaction.guild, self.Overwrite)
        self.Smartlog.UpdateEmbed()
        
        await interaction.edit_original_response(embed=self.Smartlog.Embed)

        return await super().callback(interaction)
    
class SmartlogView(discord.ui.View):
    def __init__(self, Log: Smartlog):
        super().__init__(timeout=None)

        self.Smartlog: Smartlog = Log
        self.Cancelled: bool = False

    @discord.ui.button(label="Add Data", style=discord.ButtonStyle.gray)
    async def AddData(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(SmartlogModal(self.Smartlog, False))

    @discord.ui.button(label="Overwrite Data", style=discord.ButtonStyle.gray)
    async def OverwriteData(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(SmartlogModal(self.Smartlog, True))

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