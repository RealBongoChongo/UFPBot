import discord

def MergeSmartlog(Smartlog1: dict, Smartlog2: dict) -> dict:
    for Point, Users in Smartlog2.items():
        if not str(Point) in Smartlog1:
            Smartlog1[str(Point)] = []

        for User in Users:
            Smartlog1[str(Point)].append(User)

    return Smartlog1

def ParseSmartlogMessage(Message: str) -> dict:
    MessageLines = Message.split("\n")
    Smartlog = {}

    for Line in MessageLines:
        ParsedLine = Line.split(" - ")
        if len(ParsedLine) != 2:
            continue

        try:
            Point = int(ParsedLine[0])
        except:
            continue

        Users = ParsedLine[1].split(", ")

        if not str(Point) in Smartlog:
            Smartlog[str(Point)] = []

        for User in Users:
            UserID = User.replace("<@", "").replace(">", "")

            Smartlog[str(Point)].append(int(UserID))

    return Smartlog

def SmartlogToString(Smartlog: dict) -> str:
    SmartlogList = []

    for Point, Users in Smartlog.items():
        SmartlogList.append([int(Point), Users])

    return "\n".join(sorted(SmartlogList, key=lambda x: x[0]))

async def CreateSmartlogMessage(bot: discord.Bot, ctx: discord.ApplicationContext) -> dict:
    SmartlogSuccess = False
    ParsedSmartlog = None

    while not SmartlogSuccess:
        SmartlogMessage = await bot.wait_for("message", check=lambda message: message.author == ctx.author and message.channel == ctx.channel and message.guild == ctx.guild)

        ParsedSmartlog = ParseSmartlogMessage(SmartlogMessage.content)

        SmartlogSuccess = bool(ParsedSmartlog)

    return ParsedSmartlog