import random

from player import Player

from colorama import Fore, Style

red = Fore.RED
green = Fore.GREEN
blue = Fore.BLUE
white = Fore.WHITE

def log(color, text):
    print(color + text + Style.RESET_ALL)

def take_damage(source: Player, target: Player, fight_env_list: list):
    """
    Handles a player taking damage from another player.

    Args:
        source (Player): The Player object inflicting the damage.
        target (Player): The Player object receiving the damage.
        fight_env_list (List): A list of unchangeable outside vars to inpact damage.
    """

    enrage_buff = fight_env_list[0]
    enrage_timer = fight_env_list[1]
    current_item = fight_env_list[2]

    def_mod = max(1, (enrage_buff * 0.5))

    if (target.DodgeOdds / enrage_buff) >= random.random():
        log(green, f"{target.PlayerName} dodged!")
    else:
        if source.CritRate >= random.random():
            damage_dealt = (current_item.damage * source.Atk)
            mited_damage_dealt = ((damage_dealt * enrage_buff / (target.Def / def_mod)) * source.CritDamageMod)
            mited_damage_dealt = mited_damage_dealt * random.uniform(0.95, 1.05)

            if enrage_timer.timed_out:
                log(blue, f"Crit! {source.PlayerName} {current_item.game_obj} crits {target.PlayerName} for {mited_damage_dealt:.2f} damage! Enraged")
                target.HP = target.HP - mited_damage_dealt
            else:
                log(blue, f"Crit! {source.PlayerName} {current_item.game_obj} crits {target.PlayerName} for {mited_damage_dealt:.2f} damage!")
                target.HP = target.HP - mited_damage_dealt
        else:
            damage_dealt = (current_item.damage * source.Atk)
            mited_damage_dealt = (damage_dealt * enrage_buff / (target.Def / def_mod))
            mited_damage_dealt = mited_damage_dealt * random.uniform(0.95, 1.05)
            
            if enrage_timer.timed_out:
                log(red, f"Hit! {source.PlayerName} {current_item.game_obj} hits {target.PlayerName} for {mited_damage_dealt:.2f} damage! Enraged")
                target.HP = target.HP - mited_damage_dealt
            else:
                log(red, f"Hit! {source.PlayerName} {current_item.game_obj} hits {target.PlayerName} for {mited_damage_dealt:.2f} damage!")
                target.HP = target.HP - mited_damage_dealt
        
        target.DamageTaken += mited_damage_dealt
        source.DamageDealt += mited_damage_dealt