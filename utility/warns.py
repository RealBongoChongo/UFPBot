import json

def getWarns(member):
    with open("json/warns.json", "r") as f:
        data = json.load(f)

    if str(member.id) in data:
        return data[str(member.id)]["warns"]
    else:
        return None

def deleteWarns(member):
    with open("json/warns.json", "r") as f:
        data = json.load(f)

    if member:
        if str(member.id) in data:
            data[str(member.id)]["warns"] = []
        else:
            return
    else:
        data = {}

    with open("json/warns.json", "w") as f:
        json.dump(data, f, indent=4)

def createData(member):
    with open("json/warns.json", "r") as f:
        data = json.load(f)

    if str(member.id) in data:
        return
    else:
        data[str(member.id)] = {
            "warns": [

            ]
        }

    with open("json/warns.json", "w") as f:
        json.dump(data, f, indent=4)

def createWarn(member, ruleCitation, messageLink, seniorOfficer):
    createData(member)
    with open("json/warns.json", "r") as f:
        data = json.load(f)

    data[str(member.id)]["warns"].append({
        "ruleCitation": ruleCitation,
        "messageLink": messageLink,
        "seniorOfficer": seniorOfficer.mention
    })

    with open("json/warns.json", "w") as f:
        json.dump(data, f, indent=4)

    return len(data[str(member.id)]["warns"])