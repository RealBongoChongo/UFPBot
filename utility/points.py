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
            "WaitingForPromotion": False
        }

        WriteKey(UserID, Data)

        return Data
    
    return ReadJson()[UserID]

def AddPoints(UserID: int, Points: int) -> None:
    UserData = GetUser(UserID)

    UserData["Points"] += Points

    WriteKey(str(UserID), UserData)