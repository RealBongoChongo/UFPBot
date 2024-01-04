import json

def getMessage():
    with open("json/relations.json", "r") as f:
        data = json.load(f)

    return data["message"]

def setMessage(msgId):
    with open("json/relations.json", "r") as f:
        data = json.load(f)

    data["message"] = msgId

    with open("json/relations.json", "w") as f:
        json.dump(data, f, indent=4)

def addAlly(allyName):
    with open("json/relations.json", "r") as f:
        data = json.load(f)

    if allyName in data["allies"]:
        return False
    else:
        data["allies"].append(allyName)

    with open("json/relations.json", "w") as f:
        json.dump(data, f, indent=4)

    return True

def removeAlly(allyName):
    with open("json/relations.json", "r") as f:
        data = json.load(f)

    if allyName in data["allies"]:
        data["allies"].remove(allyName)
    else:
        return False

    with open("json/relations.json", "w") as f:
        json.dump(data, f, indent=4)

    return True

def getAllies():
    with open("json/relations.json", "r") as f:
        data = json.load(f)

    return data["allies"]

def addFriendly(friendlyName):
    with open("json/relations.json", "r") as f:
        data = json.load(f)

    if friendlyName in data["friendlies"]:
        return False
    else:
        data["friendlies"].append(friendlyName)

    with open("json/relations.json", "w") as f:
        json.dump(data, f, indent=4)

    return True

def removeFriendly(friendlyName):
    with open("json/relations.json", "r") as f:
        data = json.load(f)

    if friendlyName in data["friendlies"]:
        data["friendlies"].remove(friendlyName)
    else:
        return False

    with open("json/relations.json", "w") as f:
        json.dump(data, f, indent=4)

    return True

def getFriendlies():
    with open("json/relations.json", "r") as f:
        data = json.load(f)

    return data["friendlies"]

def addEnemy(enemyName, typeOf):
    with open("json/relations.json", "r") as f:
        data = json.load(f)

    if enemyName in data["enemies"]:
        return False
    else:
        data["enemies"][enemyName] = {
            "name": enemyName,
            "type": typeOf
        }

    with open("json/relations.json", "w") as f:
        json.dump(data, f, indent=4)

    return True

def removeEnemy(enemyName):
    with open("json/relations.json", "r") as f:
        data = json.load(f)

    if enemyName in data["enemies"]:
        data["enemies"].pop(enemyName)
    else:
        return False

    with open("json/relations.json", "w") as f:
        json.dump(data, f, indent=4)

    return True

def getEnemies():
    with open("json/relations.json", "r") as f:
        data = json.load(f)

    return data["enemies"]