from karen.actions import *
from karen.state import State

def getComboSequence(inputString="", warnings=[]):

    if not ("G+u" in ACTIONS):
        loadMoveStacks()

    # removes whitespace
    inputString = "".join(inputString.split())

    # removes anything in brackets from inputString string
    sequence = inputString
    while "(" in sequence and ")" in sequence[sequence.find("("):]:
        sequence = sequence[:sequence.find("(")] + sequence[sequence[sequence.find("("):].find(")") + sequence.find("(") + 1:]

    # handles long-form by converting to list
    if ">" in sequence:
        sequence = sequence.replace("+", ">+>").split(">") # make sure '+' characters are split out as their own entries
        sequence = [x for x in sequence if x != ""] # removes empty entries caused by double '>' characters
    
    # unrecognised conditions
    warnings += [unknownAction + " is not a recognised action" for unknownAction in sequence if not unknownAction.lower() in ACTION_NAMES]
    
    # converts to a list of correctly formatted keys in ACTION_NAMES
    sequence = [(ACTION_NAMES[x] if x in ACTION_NAMES else x.lower()) for x in sequence if (x.lower() in ACTION_NAMES)] 
    sequence = list("".join(sequence))

    # folds movestack indicators into actions
    foldSequence = []
    for i in range(len(sequence)):
        if len(foldSequence) > 0 and sequence[i-1] == "+":
            foldSequence[-1] += "+" + sequence[i]
        elif sequence[i] != "+":
            foldSequence.append(sequence[i])
    
    # verify movestacks
    verifySequence = []
    for action in foldSequence:
        if action in ACTION_NAMES and ACTION_NAMES[action] in ACTIONS:
            verifySequence.append(ACTION_NAMES[action])
        else:
            warnings += [action + " is not a regocnised movestack"]
            verifySequence += action.split("+")

    return verifySequence

def addAction(state=State(), action="", nextAction="", warnings=[]):

    if not ("G+u" in ACTIONS):
        loadMoveStacks()

    # awaits required cooldowns
    for a in ACTIONS[action].awaitCharges:
        state.incrementTime(state.charges[a].activeTimer, warnings) 
        state.incrementTime(state.charges[a].cooldownTimer - ACTIONS[action].awaitCharges[a], warnings)
        state.incrementTime(state.charges[a].RECHARGE_TIME - state.charges[a].currentCharge - ACTIONS[action].awaitCharges[a], warnings)

    # awaits tracer register for GOHT
    if "g" in ACTIONS[action].awaitCharges:
        state.incrementTime(state.gohtWaitTime - ACTIONS[action].awaitCharges["g"], warnings)

    # awaits kick expiration for punch
    if "p" in action and state.punchSequence == 2:
        state.incrementTime(state.punchSequenceTimer, warnings)

    if "k" in action and state.punchSequence < 2:
        warnings += ["uses impossible kick after " + state.sequence]
    
    if "G" in action and (state.tracerActiveTimer == 0 or state.tracerActiveTimer < ACTIONS[action].awaitCharges["g"]) and (state.burnTracerActiveTimer == 0 or state.burnTracerActiveTimer < ACTIONS[action].awaitCharges["g"]):
        warnings += ["uses GOHT on nonxistent or expired tracer after " + state.sequence]

    if "p" in action and (state.hasSwingOverhead or state.hasJumpOverhead):
        warnings += ["uses punch when overhead was expected after " + state.sequence]
    if "k" in action and (state.hasSwingOverhead or state.hasJumpOverhead):
        warnings += ["uses kick when overhead was expected after " + state.sequence]

    # awaits whiff end for overhead
    if "o" in action and (not state.hasJumpOverhead) and (not state.hasSwingOverhead) and state.charges["s"].activeTimer > 0:
        state.incrementTime(state.charges["s"].activeTimer, warnings)

    # punch sequence increment
    if "p" in action:
        state.punchSequence += 1
        state.punchSequenceTimer = PUNCH_SEQUENCE_MAX_DELAY
    if "k" in action:
        state.punchSequence = 0
    
    # processes overhead logic
    if "o" in action and (not state.hasSwingOverhead) and (not state.hasJumpOverhead):
        warnings += ["uses impossible overhead after " + state.sequence]

    if action == "l":
        state.isAirborn = False
        state.hasDoubleJump = True
        state.hasSwingOverhead = False
        state.hasJumpOverhead = False
   
    if action == "j" and state.isAirborn:
        if not state.hasDoubleJump: 
            warnings += ["uses impossible double jump after " + state.sequence]
        state.hasDoubleJump = False
        state.hasJumpOverhead = True

    elif action in ["j", "s", "b"] or "u" in action:
        state.isAirborn = True

    if action == "d":
        if not state.hasDoubleJump: 
            warnings += ["uses impossible double jump after " + state.sequence]
        state.isAirborn = True
        state.hasDoubleJump = False
        state.hasJumpOverhead = True

    if action in ["o", "G", "G+u", "p+G", "k+G", "p+G+u", "k+G+u", "p+G+u", "k+G+u", "o+t", "p+o", "k+o"]:
        if state.hasSwingOverhead:
            state.hasSwingOverhead = False
        else:
            state.hasJumpOverhead = False
    if action in ["o+G", "o+G+u"]:
        state.hasSwingOverhead = False
        state.hasJumpOverhead = False
    if action == "u+w+G":
        state.hasSwingOverhead = True
        state.hasJumpOverhead = False

    if action in ["s", "b"] or "u" in action:
        state.hasDoubleJump = True
        state.hasJumpOverhead = False
    
    if action == "b":
        state.hasSwingOverhead = True

    # ends current cancellable actions
    for cancelCharge in ACTIONS[action].endActivations:
        if state.charges[cancelCharge].activeTimer > 0:
            state.endAction(cancelCharge)

    # activating actions/consuming cooldowns
    if action == "s":
        state.removeSwingOnEnd = True
    if "w" in action:
        state.removeSwingOnEnd = False

    for charge in ACTIONS[action].chargeActivations:
        state.charges[charge].cooldownTimer = state.charges[charge].COOLDOWN_TIME
        if ACTIONS[action].chargeActivations[charge] == 0:
            state.charges[charge].currentCharge -= state.charges[charge].RECHARGE_TIME
        else:
            state.charges[charge].activeTimer = ACTIONS[action].chargeActivations[charge]
        
    # adding tracer tags
    if action in ["t", "b"] and state.tracerActiveTimer == 0 and state.burnTracerActiveTimer == 0:
        state.gohtWaitTime = ACTIONS[action].damageTime
    if action == "t":
        state.tracerActiveTimer = TRACER_ACTIVE_TIME + ACTIONS["t"].damageTime
    if action == "b":
        state.burnTracerActiveTimer = BURN_TRACER_ACTIVE_TIME + ACTIONS["b"].damageTime       

    # proccing tracers
    if ACTIONS[action].procsTracer and state.tracerActiveTimer >= ACTIONS[action].procTime or action in ["p+t", "k+t", "o+t"]:
        state.damageDealt += TRACER_PROC_DAMAGE
        state.tracerActiveTimer = 0
    if ACTIONS[action].procsTracer and state.burnTracerActiveTimer >= ACTIONS[action].procTime:
        state.burnActiveTimer = BURN_TRACER_BURN_TIME + ACTIONS[action].procTime
        state.burnTracerActiveTimer = 0

    if state.firstDamageTime == 0 and ACTIONS[action].damage > 0:
        state.firstDamageTime = state.timeTaken + ACTIONS[action].firstDamageTime

    state.damageDealt += ACTIONS[action].damage
    state.incrementTime(ACTIONS[action].damageTime if nextAction == "" else ACTIONS[action].cancelTimes[nextAction], warnings)

    state.sequence += ("" if state.sequence == "" else " > ") + ACTIONS[action].name