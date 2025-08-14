from karen.evaluate import evaluate
from karen.classify import CLASSIFICATIONS

COMBO_NAMES = {
    "bnb" : "Bread & Butter (BnB)",
    "bnbplink" : "BnB Long Plink",
    "fishing" : "Fishing Combo / Sekkombo",
    "fish" : "Fishing Combo / Sekkombo",
    "sekkombo" : "Fishing Combo / Sekkombo",
    "sekombo" : "Fishing Combo / Sekkombo",
    "gripkickrip" : "Grip Kick Rip (GKR)",
    "gkr" : "Grip Kick Rip (GKR)",
    "ohburst" : "Overhead Burst",
    "fantastic" : "Fantastic Killer",
    "sapstack" : "Saporen FFAmestack",
    "agnikai" : "Agni-Kai Yo-Yo",
    "bald" : "Bald Slam",

    "burnbnb" : "Burn BnB / Fadeaway",
    "fadeaway" : "Burn BnB / Fadeaway",
    "burnohburst" : "Burn Overhead Burst",
    "burnoverhead" : "Burn Overhead Burst",
    "burnoh" : "Burn Overhead Burst",
    "friedfish" : "Fried Fish / Firehook",
    "fried" : "Fried Fish / Firehook",
    "burnsekkombo" : "Fried Fish / Firehook",
    "burnsekombo" : "Fried Fish / Firehook",
    "firehook" : "Fried Fish / Firehook",
    "innout" : "In And Out",
    "in&out" : "In And Out"
}

def loadComboNames():
    for sequence in CLASSIFICATIONS:
        filterName = CLASSIFICATIONS[sequence].replace(" ", "").replace("-", "").lower()
        if len(filterName) > 5 and filterName[-5:] == "combo":
            filterName = filterName[:-5]
        COMBO_NAMES[filterName] = CLASSIFICATIONS[sequence]

    for name in COMBO_NAMES.copy():
        if "bnb" in name:
            COMBO_NAMES[name.replace("bnb", "b&b")] = COMBO_NAMES[name]
            COMBO_NAMES[name.replace("bnb", "bandb")] = COMBO_NAMES[name]
            COMBO_NAMES[name.replace("bnb", "breadnbutter")] = COMBO_NAMES[name]
            COMBO_NAMES[name.replace("bnb", "bread&butter")] = COMBO_NAMES[name]
            COMBO_NAMES[name.replace("bnb", "breadandbutter")] = COMBO_NAMES[name]


def getCombo(name):
    if not "b&b" in COMBO_NAMES:
        loadComboNames()

    filterName = name.replace(" ", "").replace("-", "").lower()
    if len(filterName) > 5 and filterName[-5:] == "combo":
            filterName = filterName[:-5]

    if not filterName in COMBO_NAMES:
        return "```\nERROR: Combo not found\n```"
    
    for sequence in CLASSIFICATIONS:
        if CLASSIFICATIONS[sequence] == COMBO_NAMES[filterName]:
            return evaluate(sequence)
        
def listCombos():
    comboList = []
    sequenceList = []
    maxLength = 0

    for sequence in CLASSIFICATIONS:
        if not CLASSIFICATIONS[sequence] in comboList:
            comboList += [CLASSIFICATIONS[sequence]]
            sequenceList += [sequence]
            maxLength = max(maxLength, len(comboList[-1]))

    return "```\n" + "\n".join([comboList[i] + " " * (maxLength - len(comboList[i])) + " | " + sequenceList[i] for i in range(len(comboList))]) + "\n```"