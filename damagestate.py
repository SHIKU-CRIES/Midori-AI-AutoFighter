import math
import random

from player import Player

from damage_over_time import dot as damageovertimetype
from healing_over_time import hot as healingovertimetype

from colorama import Fore, Style

from themedstuff import themed_names

red = Fore.RED
green = Fore.GREEN
blue = Fore.BLUE
white = Fore.WHITE

def log(color, text):
    print(color + text + Style.RESET_ALL)
    return text

def debug_log(text):
    with open("debug_log.txt", "a") as f:
        f.write(f"\n{text}")
    
    return text

def check_passive_mod(source: Player, target: Player, mited_damage_dealt: float):
    if themed_names[0] in source.PlayerName.lower():
        if source.Regain > 1:
            source.Regain -= 0.01
            source.MHP += 500
            source.HP += 500
            source.Atk += 50
            source.Def += 50
            
            source.HOTS.append(healingovertimetype("light", round(1), 15, "generic", source.PlayerName, 2))

        if themed_names[0] in target.PlayerName.lower():
            if random.random() >= 0.98:
                log(random.choice([red, green, blue]), f"{source.PlayerName} tried to hit {target.PlayerName}! {random.choice([red, green, blue])}Why would I hit myself user... {random.choice([red, green, blue])}you think I am dumb?")
            
            mited_damage_dealt = mited_damage_dealt / 4
            
            target.HOTS.append(healingovertimetype("light", round(1), 25, "generic", source.PlayerName, 2))
            target.DodgeOdds += 0.005
        else:
            if source.HP > source.MHP * 0.25:
                hp_diff = source.HP - source.MHP * 0.25
                reduction_factor = hp_diff / (source.MHP * 0.75)
                
                scaled_reduction = reduction_factor ** 4 * 0.01

                source.HP -= round(source.MHP * scaled_reduction)

                mited_damage_dealt = mited_damage_dealt * (((source.MHP - source.HP) + 1) * 4)
                target.DOTS.append(damageovertimetype("Bleed", mited_damage_dealt, 25, "generic", source.PlayerName, 2))
            else:
                mited_damage_dealt = mited_damage_dealt * (((source.MHP - source.HP) + 1) * 2)
                target.DOTS.append(damageovertimetype("Bleed", mited_damage_dealt, 25, "generic", source.PlayerName, 1))

    if themed_names[1] in source.PlayerName.lower():
        hp_percentage = source.HP / source.MHP

        if source.DodgeOdds > 0.5:
            source.Def += source.check_base_stats(source.Def, round(source.DodgeOdds ** 2)) + round(source.DodgeOdds)
            source.DodgeOdds = 0


    elif themed_names[1] in target.PlayerName.lower():
        hp_percentage = source.HP / source.MHP

        if hp_percentage < 0.75:
            damage_reduction = (1 - hp_percentage) * 0.95
            mited_damage_dealt *= (1 - damage_reduction)

        if hp_percentage < 0.55:
            mited_damage_dealt = carly_mit_adder(target, mited_damage_dealt)

        if hp_percentage < 0.25:
            mited_damage_dealt = carly_mit_adder(target, mited_damage_dealt)
            
        
    if themed_names[2] in source.PlayerName.lower():
        pass

    if themed_names[3] in source.PlayerName.lower():
        if target.MHP > source.MHP:
            source.MHP += random.randint(5, 15)
            target.MHP -= 1

    if themed_names[4] in source.PlayerName.lower():
        pass

    if themed_names[5] in source.PlayerName.lower():
        pass

    if themed_names[6] in source.PlayerName.lower():
        pass

    if themed_names[7] in source.PlayerName.lower():
        if source.HP < source.MHP * 0.85:
            mited_damage_dealt = mited_damage_dealt + ((source.MHP / 4) / (target.Def * 2))

    if themed_names[8] in source.PlayerName.lower():
        if source.Atk > 1000:
            source.Regain += 0.05
            source.Atk -= 1
        if source.Def > 1000:
            source.Regain += 0.05
            source.Def -= 1

    if themed_names[9] in source.PlayerName.lower():
        pass
    
    return max(mited_damage_dealt, 1)

def carly_mit_adder(target: Player, mited_damage_dealt: float):
    for item in target.Items:
        if not item:
            continue
        try:
            mited_damage_dealt = item.on_damage_taken(mited_damage_dealt)
        except Exception as error:
            continue
    
    return mited_damage_dealt

def apply_damage_item_effects(source: Player, target: Player, mited_damage_dealt: float):
        
        for item in source.Items:
            if not item:
                continue
            try:
                before_damage = mited_damage_dealt
                mited_damage_dealt = item.on_damage_dealt(mited_damage_dealt)
                source.DamageDealt += int(mited_damage_dealt)
                # log(white, f"Damage Buff effect from {source.PlayerName}: {item.name}, Item Power: {item.power}, Damage Diff: {mited_damage_dealt - before_damage}")
            except Exception as error:
                continue

        for item in target.Items:
            if not item:
                continue
            try:
                before_damage = mited_damage_dealt
                mited_damage_dealt = item.on_damage_taken(mited_damage_dealt)
                target.DamageTaken += int(mited_damage_dealt)
                # log(white, f"Damage Mit effect from {target.PlayerName}: {item.name}, Item Power: {item.power}, Damage Diff: {mited_damage_dealt - before_damage}")
            except Exception as error:
                continue

        return mited_damage_dealt

def take_damage(source: Player, target: Player, fight_env_list: list, def_mod: float):
    """
    Handles a player taking damage from another player.

    Args:
        source (Player): The Player object inflicting the damage.
        target (Player): The Player object receiving the damage.
        fight_env_list (List): A list of unchangeable outside vars to inpact damage.
    """

    enrage_buff = fight_env_list[0]
    enrage_timer = fight_env_list[1]

    mited_damage_dealt = float(0)
    random_crit = random.random()
    source_vit = source.Vitality
    target_vit = target.Vitality
    def_val = ((target.Def / def_mod) ** 2)
    damage_dealt = ((source.Atk * source_vit) * 2)
    crit = False
    # log(white, f"pre mitigated dmg: {damage_dealt}, target Vit: {target_vit}, source Vit: {source_vit}, target def: {def_val}")

    if source.CritRate >= random_crit:
        crit = True
        damage_dealt = apply_damage_item_effects(source, target, damage_dealt * (enrage_buff * (source.CritDamageMod * max(1, source.CritRate))))
        mited_damage_dealt = float(damage_dealt / max(def_val * target_vit, 2))
        mited_damage_dealt = mited_damage_dealt * random.uniform(0.95, 1.05)
    else:
        damage_dealt = apply_damage_item_effects(source, target, damage_dealt * enrage_buff)
        mited_damage_dealt = float(damage_dealt / max(def_val * target_vit, 2))
        mited_damage_dealt = mited_damage_dealt * random.uniform(0.95, 1.05)
    
    mited_damage_dealt = check_passive_mod(source, target, mited_damage_dealt)

    if (target.DodgeOdds / enrage_buff) >= random.random():
        log(green, f"{target.PlayerName} dodged!")
    else:
        if crit:
            if enrage_timer.timed_out:
                log(blue, f"Crit! {source.PlayerName} crits {target.PlayerName} for {mited_damage_dealt:.2f} damage! Enraged")
            else:
                log(blue, f"Crit! {source.PlayerName} crits {target.PlayerName} for {mited_damage_dealt:.2f} damage!")
        
        else:
            if enrage_timer.timed_out:
                log(red, f"Hit! {source.PlayerName} hits {target.PlayerName} for {mited_damage_dealt:.2f} damage! Enraged")
            else:
                log(red, f"Hit! {source.PlayerName} hits {target.PlayerName} for {mited_damage_dealt:.2f} damage!")

        if mited_damage_dealt > target.HP:
            mited_damage_dealt = target.HP + 1000

        target.take_damage(max(mited_damage_dealt, 1))