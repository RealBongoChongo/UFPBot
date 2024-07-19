import discord, random, typing

characters = "a b c d e f g h i j k l m n o p q r s t u v w x y z 1 2 3 4 5 6 7 8 9 0".split()

def GenerateID() -> str:
    GeneratedID = []

    for i in range(6):
        IDChunk = ""
        for i in range(6):
            IDChunk += random.choice(characters)

        GeneratedID.append(IDChunk)

    return "-".join(GeneratedID)

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

    for Point, Users in Smartlog.copy().items():
        for UserIndex in range(len(Users)):
            Users[UserIndex] = "<@{}>".format(str(Users[UserIndex]))

        SmartlogList.append([int(Point), Users])

    SmartlogList = sorted(SmartlogList, key=lambda x: x[0], reverse=True)

    Log = []

    for LogLine in SmartlogList:
        Log.append("{} - {}".format(str(LogLine[0]), ", ".join(LogLine[1])))

    return "\n".join(Log)

async def CreateSmartlogMessage(bot: discord.Bot, ctx: discord.ApplicationContext, OldSmartlog: dict) -> typing.Union[dict, bool]:
    SmartlogSuccess = False
    ParsedSmartlog = None

    while not SmartlogSuccess:
        SmartlogMessage = await bot.wait_for("message", check=lambda message: message.author == ctx.author and message.channel == ctx.channel and message.guild == ctx.guild)

        if SmartlogMessage.content.lower() == "done":
            return OldSmartlog, True

        ParsedSmartlog = ParseSmartlogMessage(SmartlogMessage.content)

        SmartlogSuccess = bool(ParsedSmartlog)

    return ParsedSmartlog, False