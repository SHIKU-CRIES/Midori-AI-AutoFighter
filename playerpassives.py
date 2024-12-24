
import random

from player import Player

from colorama import Fore, Style

from damagestate import log
from damagestate import apply_damage_item_effects

from themedstuff import themed_names

red = Fore.RED
green = Fore.GREEN
blue = Fore.BLUE
white = Fore.WHITE

def check_passive_mod(source: Player, target: Player, mited_damage_dealt: float):
    if themed_names[0] in source.PlayerName.lower():
        if themed_names[0] in target.PlayerName.lower():
            if random.random() >= random.random():
                log(random.choice([red, green, blue]), f"{source.PlayerName} tried to hit {target.PlayerName}! {random.choice([red, green, blue])}Why would I hit myself user... {random.choice([red, green, blue])}you think I am dumb?")
            
            mited_damage_dealt = 0
            target.DodgeOdds += 0.05

        else:
            if source.HP > source.MHP * 0.35:
                source.HP -= (source.MHP * 0.01)
                target.Bleed += max(mited_damage_dealt * (source.MHP - source.HP), 55)
            else:
                target.Bleed += max(mited_damage_dealt, 1)

    if themed_names[1] in source.PlayerName.lower():
        if source.Bleed > 55:
            if random.choice([True, False]):
                source.Def += source.check_base_stats(source.Def, source.Bleed ** 2) + source.Bleed
                source.Bleed /= 2

    elif themed_names[1] in target.PlayerName.lower():
        if target.HP < target.MHP * 0.55:
            mited_damage_dealt = apply_damage_item_effects(source, target, mited_damage_dealt)
        
    if themed_names[2] in source.PlayerName.lower():
        if source.Bleed > 1:
            mited_damage_dealt = mited_damage_dealt + (10 * source.Bleed)

    if themed_names[3] in source.PlayerName.lower():
        if target.MHP > source.MHP:
            source.MHP += 10
            target.MHP -= 1

    if themed_names[4] in source.PlayerName.lower():
        pass

    if themed_names[5] in source.PlayerName.lower():
        pass

    if themed_names[6] in source.PlayerName.lower():
        pass

    if themed_names[7] in source.PlayerName.lower():
        if source.HP < source.MHP * 0.85:
            mited_damage_dealt = mited_damage_dealt + (source.MHP / 4)

    if themed_names[8] in source.PlayerName.lower():
        if source.HP != source.MHP:
            if source.Atk > 1000:
                source.Regain += 0.01
                source.Atk -= 1
            if source.Def > 1000:
                source.Regain += 0.01
                source.Def -= 1

    if themed_names[9] in source.PlayerName.lower():
        pass
    
    return mited_damage_dealt