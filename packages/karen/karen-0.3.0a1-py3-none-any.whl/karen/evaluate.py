from karen.state import State
from karen.combo import getComboSequence, addAction
from karen.classify import classify
from math import floor
from karen.actions import *

def evaluate(inputString, printWarnings = True):
    warnings = []

    state = State()
    comboSequence = getComboSequence(inputString, warnings) + [""]

    # runs a second evaluation with maximum action ranges
    maxTravelTimeState = State()
    maxTravelTimeState.inferInitialState(comboSequence)

    # infer initial state being airborne/having overhead
    state.inferInitialState(comboSequence, warnings)
    comboSequence = state.correctSequence(comboSequence)

    for i in range(len(comboSequence) - 1):
        nextAction = [j for j in comboSequence[i+1:] if not j in ["j", "d", "l"]][0]
        addAction(state, comboSequence[i], nextAction, warnings)
        addAction(maxTravelTimeState, comboSequence[i], nextAction, maxTravelTimes=True)
    state.resolve(warnings)
    maxTravelTimeState.resolve()

    # checks for continued burn tracer damage after final action
    burnTracerBonusDamage = ""
    if state.burnActiveTimer > 12:
        burnTracerBonusDamage = "(plus " + str(int(floor((state.burnActiveTimer - 1) / 12) * BURN_TRACER_DPS / 5)) +" burn over time)"

    comboName = classify("".join(comboSequence))

    output = ( f"**{comboName}**"
    f"\n> {state.sequence}"
    f"\n**Time:** {round(state.timeTaken / 60, 2)}{f"-{round(maxTravelTimeState.timeTaken / 60, 2)}" if maxTravelTimeState.timeTaken != state.timeTaken else ""} seconds ({state.timeTaken}{f"-{maxTravelTimeState.timeTaken}" if maxTravelTimeState.timeTaken != state.timeTaken else ""} frames)"
    f"{f"\n**Time From Damage:** {round(state.timeFromDamage / 60, 2)}{f"-{round(maxTravelTimeState.timeFromDamage / 60, 2)}" if maxTravelTimeState.timeFromDamage != state.timeFromDamage else ""} seconds ({state.timeFromDamage}{f"-{maxTravelTimeState.timeFromDamage}" if maxTravelTimeState.timeFromDamage != state.timeFromDamage else ""} frames)" if state.damageDealt > 0 else ""}"
    f"\n**Damage:** {int(state.damageDealt)} {burnTracerBonusDamage}" )

    

    if len(warnings) > 0 and printWarnings:
        warninglist = ["\nWARNING: " + x for x in warnings]

        output += "\n```"
        while len(warninglist) > 0 and len(output) + len(warninglist[0]) + len(f"\n...({len(warninglist)} warnings)\n```") < 2000:
            output += warninglist[0]
            warninglist = warninglist[1:]
        if len(warninglist) > 0:
            output += f"\n...({len(warninglist)} warnings)"
        output += "\n```"

    if len(output) >= 2000:
        return "```\nERROR: Combo too long for Discord API\n```"  
    
    return output