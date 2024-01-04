import json

def getUsers():
    with open("json/offduty.json", "r") as f:
        data = json.load(f)

    return data.keys()

def getData(userId):
    with open("json/offduty.json", "r") as f:
        data = json.load(f)

    return data[str(userId)]

def removeUser(userId):
    with open("json/offduty.json", "r") as f:
        data = json.load(f)

    data.pop(str(userId))

    with open("json/offduty.json", "w") as f:
        json.dump(data, f, indent=4)

def addUser(userId, estimatedEnd, eventType, endwhentext, message):
    with open("json/offduty.json", "r") as f:
        data = json.load(f)

    data[str(userId)] = {
        "estimatedEnd": estimatedEnd,
        "eventType": eventType,
        "message": message,
        "autoText": endwhentext
    }

    with open("json/offduty.json", "w") as f:
        json.dump(data, f, indent=4)

def extendUser(userId, duration):
    with open("json/offduty.json", "r") as f:
        data = json.load(f)

    data[str(userId)]["estimatedEnd"] += duration

    with open("json/offduty.json", "w") as f:
        json.dump(data, f, indent=4)

    return data[str(userId)]["estimatedEnd"]