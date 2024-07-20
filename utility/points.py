import discord, json

def ReadJson() -> dict:
    return json.load(open("json/points.json", "r"))

def WriteJson(Data) -> None:
    json.dump(Data, open("json/points.json", "w"), indent=4)

def WriteKey(Key: str, Value) -> None:
    Data = ReadJson()

    Data[Key] = Value

    WriteJson(Data)

def GetUser(UserID: int) -> dict:
    UserID = str(UserID)

    if not UserID in ReadJson():
        Data = {
            "Points": 0,
            "Notes": [],
            "Consensus": [],
            "Ranklocked": False,
            "Blacklisted": False,
            "WaitingForRankChange": False
        }

        WriteKey(UserID, Data)

        return Data
    
    return ReadJson()[UserID]

def AddPoints(UserID: int, Points: int) -> None:
    UserData = GetUser(UserID)

    UserData["Points"] += Points

    WriteKey(str(UserID), UserData)

class PointButton(discord.ui.Button):
    def __init__(self, Label: str, UserID: str):
        Colors = {
            "Promote": discord.ButtonStyle.success,
            "Minimum": discord.ButtonStyle.blurple,
            "Demote": discord.ButtonStyle.danger,
        }

        super().__init__(label=Label, custom_id="{} | {}".format(Label if Label != "Minimum" else "Restart Rank", UserID), style=Colors[Label])