import json

def getLevel():
    with open("json/srads.json", "r") as f:
        data = json.load(f)

    return data["level"]

def setLevel(level):
    with open("json/srads.json", "r") as f:
        data = json.load(f)

    data["level"] = level

    with open("json/srads.json", "w") as f:
        json.dump(data, f, indent=4)

def getWartimeChannel():
    with open("json/srads.json", "r") as f:
        data = json.load(f)

    return data["wartimeChannel"]

def setWartimeChannel(channelId):
    with open("json/srads.json", "r") as f:
        data = json.load(f)

    data["wartimeChannel"] = channelId

    with open("json/srads.json", "w") as f:
        json.dump(data, f, indent=4)