import json
import datetime

exchanges = {
    "bars": {
        "strips": 20,
        "slips": 2000
    },
    "strips": {
        "bars": 1/20,
        "slips": 100
    },
    "slips": {
        "bars": 1/2000,
        "strips": 1/100
    }
}

def getAccount(member):
    with open("json/bank.json", "r") as f:
        data = json.load(f)

    if not str(member.id) in data:
        data[str(member.id)] = {}
        data[str(member.id)]["latinum"] = {}
        data[str(member.id)]["latinum"]["slips"] = 0
        data[str(member.id)]["latinum"]["strips"] = 0
        data[str(member.id)]["latinum"]["bars"] = 0

        data[str(member.id)]["ships"] = {}
        data[str(member.id)]["equipment"] = {
            "Shield Generators": [],
            "Structural Integrity Fields": [],
            "Phasers": [],
            "Torpedo Launchers": [],
            "Deuterium Tanks": []
        }
        data[str(member.id)]["equipped"] = None
        data[str(member.id)]["thing"] = False

        with open("json/bank.json", "w") as f:
            json.dump(data, f, indent=4)

    return data[str(member.id)]

def getNetworths():
    with open("json/bank.json", "r") as f:
        data = json.load(f)

    filtered = []

    for member, account in data.items():
        net = 0
        net += account["latinum"]["bars"]
        net += exchanges["strips"]["bars"] * account["latinum"]["strips"]
        net += exchanges["slips"]["bars"] * account["latinum"]["slips"]

        filtered.append({"networth": net, "member": member})

    return filtered

def addLatinum(member, latinumtype, amount):
    with open("json/bank.json", "r") as f:
        data = json.load(f)

    data[str(member.id)]["latinum"][latinumtype] += amount
    data[str(member.id)]["latinum"][latinumtype] = int(data[str(member.id)]["latinum"][latinumtype])

    with open("json/bank.json", "w") as f:
        json.dump(data, f, indent=4)

def removeLatinum(member, latinumtype, amount):
    with open("json/bank.json", "r") as f:
        data = json.load(f)

    data[str(member.id)]["latinum"][latinumtype] -= amount
    data[str(member.id)]["latinum"][latinumtype] = int(data[str(member.id)]["latinum"][latinumtype])

    with open("json/bank.json", "w") as f:
        json.dump(data, f, indent=4)
    
def addEquipment(member, category, item):
    with open("json/bank.json", "r") as f:
        data = json.load(f)

    data[str(member.id)]["equipment"][category].append(item)

    with open("json/bank.json", "w") as f:
        json.dump(data, f, indent=4)

def addShip(member, ship):
    with open("json/bank.json", "r") as f:
        data = json.load(f)

    data[str(member.id)]["ships"][ship["name"]] = {
        "tier": ship["tier"],
        "name": ship["name"],
        "equipment": {
            "sg": None,
            "sif": None,
            "p": None,
            "tl": None,
            "dt": None
        },
        "deuterium": 0,
        "hull": 0,
        "shields": 0
    }

    with open("json/bank.json", "w") as f:
        json.dump(data, f, indent=4)

def setShipEqupped(member, ship):
    with open("json/bank.json", "r") as f:
        data = json.load(f)

    data[str(member.id)]["equipped"] = ship

    with open("json/bank.json", "w") as f:
        json.dump(data, f, indent=4)

def setEquipmentEqupped(member, category, item):
    with open("json/bank.json", "r") as f:
        data = json.load(f)

    data[str(member.id)]["equipped"]["equipment"][category] = item

    with open("json/bank.json", "w") as f:
        json.dump(data, f, indent=4)

def setShipAttribute(member, attribute, value):
    with open("json/bank.json", "r") as f:
        data = json.load(f)

    data[str(member.id)]["equipped"][attribute] = value

    with open("json/bank.json", "w") as f:
        json.dump(data, f, indent=4)

def setSetting(member, value):
    with open("json/bank.json", "r") as f:
        data = json.load(f)

    data[str(member.id)]["thing"] = value

    with open("json/bank.json", "w") as f:
        json.dump(data, f, indent=4)

def setLastMesage(member):
    with open("json/lastchats.json", "r") as f:
        data = json.load(f)

    data[str(member.id)] = int(datetime.datetime.now().timestamp())

    with open("json/lastchats.json", "w") as f:
        json.dump(data, f, indent=4)

def getMessageData():
    with open("json/lastchats.json", "r") as f:
        data = json.load(f)

    return data

def getActivity():
    with open("json/member.json", "r") as f:
        data = json.load(f)

    return data

def setActivity(total, commissioned, active, reserve, visitor, ambassador, timestamp):
    with open("json/member.json", "r") as f:
        data = json.load(f)

    data["total"] = data["total"][-29:]
    data["total"].append(total)

    data["totalCommed"] = data["totalCommed"][-29:]
    data["totalCommed"].append(commissioned)

    data["activeCommed"] = data["activeCommed"][-29:]
    data["activeCommed"].append(active)

    data["reserveCommed"] = data["reserveCommed"][-29:]
    data["reserveCommed"].append(reserve)
    
    data["visitors"] = data["visitors"][-29:]
    data["visitors"].append(visitor)

    data["ambassadors"] = data["ambassadors"][-29:]
    data["ambassadors"].append(ambassador)

    data["timestamp"] = timestamp

    with open("json/member.json", "w") as f:
        json.dump(data, f, indent=4)

def getProgression(member):
    with open("json/progressions.json") as f:
        data = json.load(f)

    if not str(member.id) in data:
        data[str(member.id)] = {
            "offenses": 0,
            "nextRefresh": None
        }

        with open("json/progressions.json", "w") as f:
            json.dump(data, f, indent=4)

    return data[str(member.id)]

def addProgression(member):
    with open("json/progressions.json") as f:
        data = json.load(f)

    if not data[str(member.id)]["nextRefresh"]:
        data[str(member.id)]["nextRefresh"] = datetime.datetime.now().timestamp() + 86400
    elif data[str(member.id)]["nextRefresh"] <= datetime.datetime.now().timestamp():
        data[str(member.id)]["nextRefresh"] = None
        data[str(member.id)]["offenses"] = 0

    if data[str(member.id)]["offenses"] < 3:
        data[str(member.id)]["offenses"] += 1
    
    with open("json/progressions.json", "w") as f:
        json.dump(data, f, indent=4)

    return data[str(member.id)]["offenses"]