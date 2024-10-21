import os
import sys
import uuid
import random

import pickle

from weapons import WeaponType
from weapons import get_weapon

from themedstuff import themed_ajt
from themedstuff import themed_names

class Player:
    def __init__(self, name):
        """
        Initializes a new player character.
        """
        self.PlayerName: str = name
        self.level: int = 1
        self.MHP: int = 1000 * self.level
        self.HP: int = self.MHP
        self.Def: int = 25
        self.Atk: int = 250
        self.Regain: float = 0.02
        self.Vitality: float = 1
        self.Bleed: float = 0
        self.CritRate: float = 0.03
        self.CritDamageMod: float = 2
        self.DodgeOdds: float = 0.03
        self.DamageTaken: int = 0
        self.DamageDealt: int = 0
        self.RushStat: int = 3
        self.Inv: list[WeaponType] = [get_weapon('game_bit')]
        self.Items: list = []
        

    def save(self):
        with open(f'{self.PlayerName}.dat', 'wb') as f:
            pickle.dump(self.__dict__, f)

    def load(self):
        try:
            with open(f'{self.PlayerName}.dat', 'rb') as f:
                self.__dict__ = pickle.load(f)
        except FileNotFoundError:
            print(f"Save file for {self.PlayerName} not found. Starting new game.")
        except Exception as e:
            print(f"Error loading save file: {e}")

    def load_past_lives(self):
        past_lives_folder = "past_lives"
        if not os.path.exists(past_lives_folder):
            os.makedirs(past_lives_folder)
            print("No past lives found.")
            return

        for filename in os.listdir(past_lives_folder):
            if filename.endswith(".pastlife"):
                filepath = os.path.join(past_lives_folder, filename)
                try:
                    with open(filepath, 'rb') as f:
                        past_life_data = pickle.load(f)

                    self.MHP: int = self.MHP + int(past_life_data['MHP'] / 10000) + 1000
                    self.HP: int = self.MHP
                    self.Def: int = self.Def + int(past_life_data['Def'] / 1000) + 100
                    self.Atk: int = self.Atk + int(past_life_data['Atk'] / 1000) + 200
                    self.Regain: float = self.Regain + float(past_life_data['Regain'] * 0.001) + 0.01
                    self.CritRate: float = self.CritRate + float(past_life_data['CritRate'] * 0.001) + 0.01
                    self.CritDamageMod: float = self.CritDamageMod + float(past_life_data['CritDamageMod'] * 0.0003) + 0.001
                    self.DodgeOdds: float = self.DodgeOdds + float(past_life_data['DodgeOdds'] * 0.0025) + 0.01

                    print(f"Loaded past life from {filename}: {past_life_data}")


                except Exception as e:
                    print(f"Error loading past life from {filename}: {e}")
                    print(f"Past life data: {past_life_data}")
                    continue
        
        number_of_past_lives = int(len([filename for filename in os.listdir(past_lives_folder) if filename.endswith(".pastlife")]) / 2)
        self.level = number_of_past_lives

    def save_past_life(self):
        past_lives_folder = "past_lives"
        if not os.path.exists(past_lives_folder):
            os.makedirs(past_lives_folder)

        # Generate a UUID for the past life file
        past_life_id = str(uuid.uuid4())
        past_life_filename = os.path.join(past_lives_folder, f"{past_life_id}.pastlife")

        # Save the current state as a past life
        try:
            with open(past_life_filename, 'wb') as f:
                pickle.dump(self.__dict__, f)
            print(f"Saved past life to {past_life_filename}")
        except Exception as e:
            print(f"Error saving past life: {e}")


        # Remove the .dat file
        try:
            os.remove(f'{self.PlayerName}.dat')
        except FileNotFoundError:
            pass  # Ignore if the file doesn't exist


    def update_inv(self, item: int, add: bool):
        if add:
            self.Inv.append(item)
        else:
            self.Inv.remove(item)
    
#themed_ajt = ["atrocious", "baneful", "barbaric", "beastly", "belligerent", "bloodthirsty", "brutal", "callous", "cannibalistic", "cowardly", "cruel", "cunning", "dangerous", "demonic", "depraved", "destructive", "diabolical", "disgusting", "dishonorable", "dreadful", "eerie", "evil", "execrable", "fiendish", "filthy", "foul", "frightening", "ghastly", "ghoulish", "gruesome", "heinous", "hideous", "homicidal", "horrible", "hostile", "inhumane", "insidious", "intimidating", "malevolent", "malicious", "monstrous", "murderous", "nasty", "nefarious", "noxious", "obscene", "odious", "ominous", "pernicious", "perverted", "poisonous", "predatory", "premeditated", "primal", "primitive", "profane", "psychopathic", "rabid", "relentless", "repulsive", "ruthless", "sadistic", "savage", "scary", "sinister", "sociopathic", "spiteful", "squalid", "terrifying", "threatening", "treacherous", "ugly", "unholy", "venomous", "vicious", "villainous", "violent", "wicked", "wrongful", "xenophobic"]
#themed_names = ["luna", "carly", "becca", "ally", "hilander", "chibi"]

    def check_name_mod(self):
        if themed_names[0] in self.PlayerName.lower():
            dodge_buff = 0.010
            max_hp_debuff = random.randint(250, 2000)
            while self.MHP > max_hp_debuff:
                dodge_buff = dodge_buff + 0.00001
                self.MHP = self.MHP - 1

            self.Atk = int(self.Atk * 1)
            self.Def = int(self.Def * 8)
            self.DodgeOdds = dodge_buff * self.level

        if themed_names[1] in self.PlayerName.lower():
            self.Atk = int(self.Atk / 25)
            self.Def = int(self.Def * 4)
            self.CritDamageMod = self.CritDamageMod * ((0.0001 * self.level) + 1)

        if themed_names[2] in self.PlayerName.lower():
            self.MHP = int(self.MHP / 2)
            self.Atk = int(self.Atk * 8)
            self.CritRate = 0

        if themed_names[3] in self.PlayerName.lower():
            self.Atk = int(self.Atk * 1.5)
            self.Def = int(self.Def * 1.5)
            self.CritDamageMod = self.CritDamageMod * ((0.005 * self.level) + 1)
            self.DodgeOdds = 0

        if themed_names[4] in self.PlayerName.lower():
            self.Atk = int(self.Atk * 1.5)
            self.Def = int(self.Def * 0.5) + 1
            self.CritRate = self.CritRate + 1
            self.CritDamageMod = self.CritDamageMod * ((0.035 * self.level) + 1)

        if themed_ajt[0] in self.PlayerName.lower(): # atrocious
            self.MHP = int(self.MHP * 1.9)
            self.Atk = int(self.Atk * 1.1)

        if themed_ajt[1] in self.PlayerName.lower(): # baneful
            self.Atk = int(self.Atk * 1.95)
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[2] in self.PlayerName.lower(): # barbaric
            self.MHP = int(self.MHP * 1.1)
            self.Def = int(self.Def * 1.9)

        if themed_ajt[3] in self.PlayerName.lower(): # beastly
            self.MHP = int(self.MHP * 1.05)
            self.Atk = int(self.Atk * 1.05)

        if themed_ajt[4] in self.PlayerName.lower(): # belligerent
            self.DodgeOdds = self.DodgeOdds * 1.9
            self.Atk = int(self.Atk * 1.1)

        if themed_ajt[5] in self.PlayerName.lower(): # bloodthirsty
            self.MHP = int(self.MHP - (self.MHP * 0.1))
            self.Atk = int(self.Atk + (self.Atk * 0.2))

        if themed_ajt[6] in self.PlayerName.lower(): # brutal
            self.CritRate = self.CritRate + 0.1
            self.DodgeOdds = self.DodgeOdds * 1.9

        if themed_ajt[7] in self.PlayerName.lower(): # callous
            self.Def = int(self.Def * 1.1)
            self.DodgeOdds = self.DodgeOdds * 1.9

        if themed_ajt[8] in self.PlayerName.lower(): # cannibalistic
            self.MHP = int(self.MHP + (self.MHP * 0.05))

        if themed_ajt[9] in self.PlayerName.lower(): # cowardly
            self.MHP = int(self.MHP * 1.2)
            self.Atk = int(self.Atk * 0.8)

        if themed_ajt[10] in self.PlayerName.lower(): # cruel
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[11] in self.PlayerName.lower(): # cunning
            self.DodgeOdds = self.DodgeOdds * 1.1

        if themed_ajt[12] in self.PlayerName.lower(): # dangerous
            self.Atk = int(self.Atk * 1.05)
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[13] in self.PlayerName.lower(): # demonic
            self.MHP = int(self.MHP * 1.9)
            self.Atk = int(self.Atk * 1.15)

        if themed_ajt[14] in self.PlayerName.lower(): # depraved
            self.Def = int(self.Def - (self.Def * 0.1))
            self.Atk = int(self.Atk + (self.Atk * 0.1))

        if themed_ajt[15] in self.PlayerName.lower(): # destructive
            self.Atk = int(self.Atk * 1.1)
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[16] in self.PlayerName.lower(): # diabolical
            self.Atk = int(self.Atk * 1.1)
            self.DodgeOdds = self.DodgeOdds * 1.9

        if themed_ajt[17] in self.PlayerName.lower(): # disgusting
            self.Def = int(self.Def * 1.9)

        if themed_ajt[18] in self.PlayerName.lower(): # dishonorable
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)

        if themed_ajt[19] in self.PlayerName.lower(): # dreadful
            self.Atk = int(self.Atk * 1.05)

        if themed_ajt[20] in self.PlayerName.lower(): # eerie
            self.DodgeOdds = self.DodgeOdds * 1.05

        if themed_ajt[21] in self.PlayerName.lower(): # evil
            self.MHP = int(self.MHP * 1.95)
            self.Atk = int(self.Atk * 1.05)

        if themed_ajt[22] in self.PlayerName.lower(): # execrable
            self.MHP = int(self.MHP * 1.9)

        if themed_ajt[23] in self.PlayerName.lower(): # fiendish
            self.DodgeOdds = self.DodgeOdds * 1.9
            self.CritRate = self.CritRate + 0.1

        if themed_ajt[24] in self.PlayerName.lower(): # filthy
            self.Def = int(self.Def * 1.95)

        if themed_ajt[25] in self.PlayerName.lower(): # foul
            self.Def = int(self.Def * 1.95)
            self.DodgeOdds = self.DodgeOdds * 1.95

        if themed_ajt[26] in self.PlayerName.lower(): # frightening
            self.Atk = int(self.Atk * 1.05)
            self.DodgeOdds = self.DodgeOdds * 1.95

        if themed_ajt[27] in self.PlayerName.lower(): # ghastly
            self.MHP = int(self.MHP * 1.95)
            self.DodgeOdds = self.DodgeOdds * 1.05

        if themed_ajt[28] in self.PlayerName.lower(): # ghoulish
            self.MHP = int(self.MHP * 1.95)
            self.Atk = int(self.Atk * 1.05)

        if themed_ajt[29] in self.PlayerName.lower(): # gruesome
            self.Atk = int(self.Atk * 1.05)
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[30] in self.PlayerName.lower(): # heinous
            self.Atk = int(self.Atk * 1.1)
            self.CritDamageMod = self.CritDamageMod * 1.1

        if themed_ajt[31] in self.PlayerName.lower(): # hideous
            self.Def = int(self.Def * 1.9)
            self.MHP = int(self.MHP * 1.1)

        if themed_ajt[32] in self.PlayerName.lower(): # homicidal
            self.Atk = int(self.Atk * 1.15)

        if themed_ajt[33] in self.PlayerName.lower(): # horrible
            self.Atk = int(self.Atk * 1.02)
            self.CritRate = self.CritRate + 0.02

        if themed_ajt[34] in self.PlayerName.lower(): # hostile
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)

        if themed_ajt[35] in self.PlayerName.lower(): # inhumane
            self.CritDamageMod = self.CritDamageMod * 1.1

        if themed_ajt[36] in self.PlayerName.lower(): # insidious
            self.Atk = int(self.Atk * 1.05)
            self.DodgeOdds = self.DodgeOdds * 1.05

        if themed_ajt[37] in self.PlayerName.lower(): # intimidating
            self.Atk = int(self.Atk * 1.95)
            self.Def = int(self.Def * 1.05)

        if themed_ajt[38] in self.PlayerName.lower(): # malevolent
            self.CritDamageMod = self.CritDamageMod * 1.05
            self.DodgeOdds = self.DodgeOdds * 1.95

        if themed_ajt[39] in self.PlayerName.lower(): # malicious
            self.Atk = int(self.Atk * 1.07)

        if themed_ajt[40] in self.PlayerName.lower(): # monstrous
            self.MHP = int(self.MHP * 1.1)
            self.Atk = int(self.Atk * 1.1)

        if themed_ajt[41] in self.PlayerName.lower(): # murderous
            self.CritRate = self.CritRate + 0.15

        if themed_ajt[42] in self.PlayerName.lower(): # nasty
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)
            self.DodgeOdds = self.DodgeOdds * 1.95

        if themed_ajt[43] in self.PlayerName.lower(): # nefarious
            self.CritRate = self.CritRate + 0.05
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[44] in self.PlayerName.lower(): # noxious
            self.Atk = int(self.Atk * 1.05)
            self.MHP = int(self.MHP * 1.95)

        if themed_ajt[45] in self.PlayerName.lower(): # obscene
            self.Def = int(self.Def * 1.9)
            self.DodgeOdds = self.DodgeOdds * 1.9

        if themed_ajt[46] in self.PlayerName.lower(): # odious
            self.Def = int(self.Def * 1.95)

        if themed_ajt[47] in self.PlayerName.lower(): # ominous
            self.CritRate = self.CritRate + 0.02
            self.CritDamageMod = self.CritDamageMod * 1.03

        if themed_ajt[48] in self.PlayerName.lower(): # pernicious
            self.MHP = int(self.MHP * 1.95)
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[49] in self.PlayerName.lower(): # perverted
            self.Def = int(self.Def * 1.9)
            self.DodgeOdds = self.DodgeOdds * 1.1

        if themed_ajt[50] in self.PlayerName.lower(): # poisonous
            self.Atk = int(self.Atk * 1.07)
            self.MHP = int(self.MHP * 1.93)

        if themed_ajt[51] in self.PlayerName.lower(): # predatory
            self.DodgeOdds = self.DodgeOdds * 1.1
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[52] in self.PlayerName.lower(): # premeditated
            self.CritRate = self.CritRate + 0.1

        if themed_ajt[53] in self.PlayerName.lower(): # primal
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)
            self.MHP = int(self.MHP * 1.05)

        if themed_ajt[54] in self.PlayerName.lower(): # primitive
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)

        if themed_ajt[55] in self.PlayerName.lower(): # profane
            self.MHP = int(self.MHP * 1.9)
            self.CritDamageMod = self.CritDamageMod * 1.1

        if themed_ajt[56] in self.PlayerName.lower(): # psychopathic
            self.DodgeOdds = self.DodgeOdds * 1.9
            self.Atk = int(self.Atk * 1.1)
            self.CritDamageMod = self.CritDamageMod * 1.1

        if themed_ajt[57] in self.PlayerName.lower(): # rabid
            self.Atk = int(self.Atk * 1.1)
            self.Def = int(self.Def * 1.9)

        if themed_ajt[58] in self.PlayerName.lower(): # relentless
            self.DodgeOdds = self.DodgeOdds * 1.9
            self.Atk = int(self.Atk * 1.05)
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[59] in self.PlayerName.lower(): # repulsive
            self.Def = int(self.Def * 1.9)
            self.DodgeOdds = self.DodgeOdds * 1.1

        if themed_ajt[60] in self.PlayerName.lower(): # ruthless
            self.CritDamageMod = self.CritDamageMod * 1.15

        if themed_ajt[61] in self.PlayerName.lower(): # sadistic
            self.Atk = int(self.Atk * 1.02)
            self.CritDamageMod = self.CritDamageMod * 1.08

        if themed_ajt[62] in self.PlayerName.lower(): # savage
            self.Atk = int(self.Atk * 1.1)
            self.Def = int(self.Def * 1.9)
            self.MHP = int(self.MHP * 1.1)

        if themed_ajt[63] in self.PlayerName.lower(): # scary
            self.Atk = int(self.Atk * 1.95)
            self.DodgeOdds = self.DodgeOdds * 1.05
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[64] in self.PlayerName.lower(): # sinister
            self.DodgeOdds = self.DodgeOdds * 1.05
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[65] in self.PlayerName.lower(): # sociopathic
            self.DodgeOdds = self.DodgeOdds * 1.9
            self.Atk = int(self.Atk * 1.15)

        if themed_ajt[66] in self.PlayerName.lower(): # spiteful
            self.Atk = int(self.Atk * 1.07)
            self.MHP = int(self.MHP * 1.93)

        if themed_ajt[67] in self.PlayerName.lower(): # squalid
            self.Def = int(self.Def * 1.95)
            self.MHP = int(self.MHP * 1.05)

        if themed_ajt[68] in self.PlayerName.lower(): # terrifying
            self.Atk = int(self.Atk * 1.9)
            self.Def = int(self.Def * 1.1)

        if themed_ajt[69] in self.PlayerName.lower(): # threatening
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)
            self.DodgeOdds = self.DodgeOdds * 1.95

        if themed_ajt[70] in self.PlayerName.lower(): # treacherous
            self.Atk = int(self.Atk * 1.05)
            self.DodgeOdds = self.DodgeOdds * 1.05
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[71] in self.PlayerName.lower(): # ugly
            self.Def = int(self.Def * 1.1)
            self.MHP = int(self.MHP * 1.9)

        if themed_ajt[72] in self.PlayerName.lower(): # unholy
            self.MHP = int(self.MHP * 25)
            self.Atk = int(self.Atk * 10)
            self.CritDamageMod = self.CritDamageMod * 5

        if themed_ajt[73] in self.PlayerName.lower(): # venomous
            self.Atk = int(self.Atk * 1.1)
            self.MHP = int(self.MHP * 1.9)

        if themed_ajt[74] in self.PlayerName.lower(): # vicious
            self.Atk = int(self.Atk * 1.1)
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[75] in self.PlayerName.lower(): # villainous
            self.Atk = int(self.Atk * 1.05)
            self.DodgeOdds = self.DodgeOdds * 1.95
            self.CritRate = self.CritRate + 0.05

        if themed_ajt[76] in self.PlayerName.lower(): # violent
            self.Atk = int(self.Atk * 1.15)
            self.Def = int(self.Def * 0.85)

        if themed_ajt[77] in self.PlayerName.lower(): # wicked
            self.Atk = int(self.Atk * 1.08)
            self.CritDamageMod = self.CritDamageMod * 1.02

        if themed_ajt[78] in self.PlayerName.lower(): # wrongful
            self.Atk = int(self.Atk * 1.05)
            self.Def = int(self.Def * 1.95)
            self.CritDamageMod = self.CritDamageMod * 1.05

        if themed_ajt[79] in self.PlayerName.lower(): # xenophobic
            self.Def = int(self.Def * 1.1)

    def check_stats(self):
        max_dodgeodds = 500
        max_crit_rate = 1

        while self.CritRate > (max_crit_rate + 0.01):
            self.Atk = self.Atk + 5
            self.CritDamageMod = self.CritDamageMod + 0.0005
            self.CritRate = self.CritRate - 0.0001

        if self.CritRate > max_crit_rate:
            self.CritRate = max_crit_rate

        while self.DodgeOdds > (max_dodgeodds + 0.01):
            self.Def = self.Def + 5
            self.DodgeOdds = self.DodgeOdds - 0.001

        if self.DodgeOdds > max_dodgeodds:
            self.DodgeOdds = max_dodgeodds

    def level_up(self, mod=1):
        """
        Levels up the player by 1 and allows the user to choose which stat to increase.
        """
        from gamestates import display_stats_menu
        self.level += 1

        mod_fixed = (mod * 0.001) + 1
        int_mod = int(mod_fixed)

        hp_up: int = random.randint(100 * self.level, 25240 * self.level) * int_mod
        def_up: int = random.randint(5 * self.level, 20 * self.level) * int_mod
        atk_up: int = random.randint(25 * self.level, 125 * self.level) * int_mod
        regain_up: float = random.uniform(0.001 * self.level, 0.005 * self.level) * mod_fixed
        critrate_up: float = random.uniform(0.001 * self.level, 0.0025 * self.level) * mod_fixed
        critdamage_up: float = random.uniform(0.004 * self.level, 0.008 * self.level) * mod_fixed
        dodgeodds_up: float = random.uniform(0.0001 * self.level, 0.0002 * self.level) * mod_fixed

        # Autopick logic
        if os.path.exists("auto.pick"):
            choice = 9
        else:
            choice = display_stats_menu(f"{hp_up:.2f}", f"{def_up:.2f}", f"{atk_up:.2f}", f"{regain_up * 100:.2f}", f"{critrate_up * 100:.2f}%", f"{critdamage_up * 100:.2f}%", f"{dodgeodds_up * 100:.2f}%", self.DamageTaken, self.DamageDealt)

        if choice == 1:
            self.MHP += int(hp_up)
            self.HP += int(hp_up)
        elif choice == 2:
            self.Def += int(def_up)
        elif choice == 3:
            self.Atk += int(atk_up)
        elif choice == 5:
            self.Regain += regain_up
        elif choice == 6:
            self.CritRate += critrate_up
        elif choice == 7:
            self.CritDamageMod += critdamage_up
        elif choice == 8:
            self.DodgeOdds += dodgeodds_up
        elif choice == 9:
            self.MHP += int(hp_up / 10)
            self.HP += int(hp_up / 10)
            self.Def += int(def_up / 5)
            self.Atk += int(atk_up / 5)
            self.Regain += regain_up / 2
            self.CritRate += critrate_up / 10
            self.CritDamageMod += critdamage_up / 10
            self.DodgeOdds += dodgeodds_up / 2

        self.check_stats()
    
    def set_level(self, level):
        self.level = level
        self.MHP: int = random.randint(25 * self.level, 45 * self.level) + 1000
        self.HP: int = self.MHP
        self.Def: int = self.Def + int(self.MHP * (0.00005 * self.level)) + 200
        self.Atk: int = random.randint(5 * self.level, 15 * self.level) + (self.level * 10)
        self.Regain: float = random.uniform(0.0001 * self.level, (self.level * 0.002)) + (self.level * 0.004)
        self.CritRate: float = random.uniform(0.001 * self.level, (self.level * 0.002)) + (self.level * 0.001)
        self.CritDamageMod: float = 2 + (self.level * 0.0025)
        self.DodgeOdds: float = 0.03 + (self.level * 0.0001)

        if level > 10:
            self.MHP = self.MHP + (2 * level)
            self.Atk = self.Atk + (20 * level)
            self.Vitality = self.Vitality + (0.001 * level)
            
            # Apply bonus every xyz levels past 10
            xyz = 25
            bonus_levels = (level - 10) // xyz
            self.MHP = self.MHP + (2 * bonus_levels)
            self.Atk = self.Atk + (20 * bonus_levels)

        if level > 20:
            self.MHP = self.MHP + (5 * level)
            self.Atk = self.Atk + (45 * level)
            self.Def = self.Def + (5 * level)
            self.Vitality = self.Vitality + (0.001 * level)
            self.CritRate = self.CritRate + 0.01

        if level > 50:
            self.MHP = self.MHP + (25 * level)
            self.Atk = self.Atk + (90 * level)
            self.Def = self.Def + (15 * level)
            self.Vitality = self.Vitality + (0.001 * level)
            self.CritRate = self.CritRate + 0.05

        if level > 100:
            self.MHP = self.MHP + (75 * level)
            self.Atk = self.Atk + (180 * level)
            self.Def = self.Def + (30 * level)
            self.Vitality = self.Vitality + (0.001 * level)
            self.CritRate = self.CritRate + 0.1

        if level > 200:
            self.MHP = self.MHP + (150 * level)
            self.Atk = self.Atk + (250 * level)
            self.Def = self.Def + (60 * level)
            self.Vitality = self.Vitality + (0.001 * level)
            self.CritRate = self.CritRate + 0.2

        self.check_name_mod()
        self.check_stats()

        self.HP = self.MHP

        print(f"Name: {self.PlayerName}")
        print(f"Level: {self.level}")
        print(f"MHP: {self.MHP}")
        print(f"HP: {self.HP}")
        print(f"Defense: {self.Def}")
        print(f"Attack: {self.Atk}")
        print(f"Regain: {self.Regain}")
        print(f"Vitality: {self.Vitality}")
        print(f"Crit Rate: {self.CritRate}")
        print(f"Crit Damage Modifier: {self.CritDamageMod}")
        print(f"Dodge Odds: {self.DodgeOdds}")