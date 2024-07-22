import json, random, discord

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
    return json.load(open("json/events.json", "r"))

def WriteJson(Data) -> None:
    json.dump(Data, open("json/events.json", "w"), indent=4)

def WriteKey(Key: str, Value) -> None:
    Data = ReadJson()

    Data[Key] = Value

    WriteJson(Data)

def CreateEvent(EventType: str, EventTimestamp: int, EventHost: discord.Member, EventNotes: str, EventDuration: int) -> str:
    EventID = GenerateID()

    WriteKey(EventID, {
        "EventHost": EventHost.id,
        "EventTimestamp": EventTimestamp,
        "EventNotes": EventNotes,
        "EventType": EventType,
        "EventDuration": EventDuration,
        "Reminded": False,
        "Announced": False
    })

    return EventID

def EditEvent(EventID: str, EventType: str=None, EventTimestamp: int=None, EventNotes: str=None, EventDuration: int=None) -> dict:
    Event = GetEvent(EventID)

    EventData = {
        "EventHost": Event["EventHost"],
        "EventTimestamp": EventTimestamp or Event["EventTimestamp"],
        "EventNotes": EventNotes or Event["EventNotes"],
        "EventType": EventType or Event["EventType"],
        "EventDuration": EventDuration or Event["EventDuration"],
        "Reminded": False or Event["Reminded"],
        "Announced": False or Event["Announced"]
    }

    WriteKey(EventID, EventData)

    return EventData

def GetEvent(EventID) -> dict:
    if not EventID in ReadJson():
        return None

    return ReadJson()[EventID]

def DeleteEvent(EventID) -> None:
    Data = ReadJson()

    Data.pop(EventID)

    WriteJson(Data)