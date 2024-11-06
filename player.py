import os
import sys
import uuid
import random

import pickle

from weapons import WeaponType
from weapons import get_weapon

from load_photos import resource_path

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
        self.Logs: list = []
        self.Inv: list[WeaponType] = [get_weapon('game_bit')]
        self.Items: list = []
        self.photo: str = "player.png"
        

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

    def set_photo(self, photo):
        if os.path.exists(resource_path(os.path.join("photos", f"{photo}.png"))):
            self.photo: str = resource_path(os.path.join("photos", f"{photo}.png"))
        else:
            photos = os.listdir(resource_path(os.path.join("photos", "fallbacks")))
            self.photo: str = resource_path(os.path.join(os.path.join("photos", "fallbacks"), f"{random.choice(photos)}"))

    def load_mimic(self):
        for filename in os.listdir("."):
            if ".dat" in filename.lower():
                try:
                    with open(f'{filename}', 'rb') as f:
                        self.__dict__ = pickle.load(f)
                except FileNotFoundError:
                    print(f"Save file for {filename} not found. Error...")
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

                    self.MHP: int = self.MHP + int(past_life_data['MHP'] / 10000) + 100
                    self.HP: int = self.MHP
                    self.Def: int = self.Def + int(past_life_data['Def'] / 1000) + 100
                    self.Atk: int = self.Atk + int(past_life_data['Atk'] / 1000) + 200
                    self.Regain: float = self.Regain + float(past_life_data['Regain'] * 0.001) + 0.01
                    self.CritRate: float = self.CritRate + float(past_life_data['CritRate'] * 0.001) + 0.01
                    self.CritDamageMod: float = self.CritDamageMod + float(past_life_data['CritDamageMod'] * 0.0003) + 0.001
                    self.DodgeOdds: float = self.DodgeOdds + float(past_life_data['DodgeOdds'] * 0.0025) + 0.01

                    if past_life_data['Vitality'] < 0:
                        print("Vitality is negative. Deleting past life file.")
                        os.remove(filename)

                    elif past_life_data['Vitality'] > 1.0000001:
                        self.Vitality = self.Vitality + ((past_life_data['Vitality'] - 1) / self.Vitality)
                    
                    self.check_stats()

                    print(f"Loaded past life from {filename}: {past_life_data}")


                except Exception as e:
                    print(f"Error loading past life from {filename}: {e}")
                    print(f"Past life data: {past_life_data}")
                    continue
        
        number_of_past_lives = int(len([filename for filename in os.listdir(past_lives_folder) if filename.endswith(".pastlife")]) / 5)
        self.level = max(number_of_past_lives, 1)

    def save_past_life(self):
        past_lives_folder = "past_lives"

        if not os.path.exists(past_lives_folder):
            os.makedirs(past_lives_folder)

        # Generate a UUID for the past life file
        past_life_id = str(uuid.uuid4())
        past_life_filename = os.path.join(past_lives_folder, f"{past_life_id}.pastlife")

        self.Logs = []

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


    def update_inv(self, item: WeaponType, add: bool):
        if add:
            self.Inv.append(item)
        else:
            self.Inv.remove(item)

    def gain_crit_rate(self, points):
        """Increases crit rate based on points, with increasing cost.

        Every 1 crit rate increase costs 100x more points.
        """
        to_be_lowered_by = 100
        current_rate = self.CritRate

        if current_rate > 1:
            desired_increase = points / ((to_be_lowered_by * (current_rate // 2)) + 1)
        else:
            desired_increase = points

        self.CritRate = current_rate + desired_increase

    def gain_crit_damage(self, points):
        """Increases crit damage based on points, with increasing cost.

        Every 10 crit damage increase costs 100x more points.
        """
        current_damage = self.CritDamageMod
        to_be_lowered_by = 100

        if current_damage > 10:
            desired_increase = points / ((to_be_lowered_by * (current_damage // 10)) + 1)
        else:
            desired_increase = points

        self.CritDamageMod += desired_increase 

#themed_ajt = ["atrocious", "baneful", "barbaric", "beastly", "belligerent", "bloodthirsty", "brutal", "callous", "cannibalistic", "cowardly", "cruel", "cunning", "dangerous", "demonic", "depraved", "destructive", "diabolical", "disgusting", "dishonorable", "dreadful", "eerie", "evil", "execrable", "fiendish", "filthy", "foul", "frightening", "ghastly", "ghoulish", "gruesome", "heinous", "hideous", "homicidal", "horrible", "hostile", "inhumane", "insidious", "intimidating", "malevolent", "malicious", "monstrous", "murderous", "nasty", "nefarious", "noxious", "obscene", "odious", "ominous", "pernicious", "perverted", "poisonous", "predatory", "premeditated", "primal", "primitive", "profane", "psychopathic", "rabid", "relentless", "repulsive", "ruthless", "sadistic", "savage", "scary", "sinister", "sociopathic", "spiteful", "squalid", "terrifying", "threatening", "treacherous", "ugly", "unholy", "venomous", "vicious", "villainous", "violent", "wicked", "wrongful", "xenophobic"]
#themed_names = ["luna", "carly", "becca", "ally", "hilander", "chibi", "mimic", "mezzy", "graygray"]

    def check_name_mod(self):
        if themed_names[0] in self.PlayerName.lower():
            dodge_buff = 0.010
            max_hp_debuff = self.MHP / 8

            while self.MHP > max_hp_debuff:
                dodge_buff = dodge_buff + 0.0000008
                self.MHP = self.MHP - 1

            self.Atk = int(self.Atk * 1)
            self.Def = int(self.Def * 2)
            self.gain_crit_rate(0.01 * self.level)
            self.DodgeOdds = self.DodgeOdds + (dodge_buff * self.level)

        if themed_names[1] in self.PlayerName.lower():
            max_hp_debuff = self.MHP / 2
            max_crit_rate = self.CritRate / 100
            max_atk_stat = self.Atk / 100
            max_def_stat = random.randint(10000000, 50000000)

            while self.MHP > max_hp_debuff:
                self.Def = self.Def + 1
                self.MHP = self.MHP - 1

            while self.CritRate > max_crit_rate:
                self.Def = self.Def + 1
                self.CritRate = self.CritRate / 2

            while self.Atk > max_atk_stat:
                self.Def = self.Def + 1
                self.Atk = self.Atk - 1

            while self.Regain > 0.1:
                self.Def = self.Def + 5
                self.Regain = self.Regain - 0.001

            self.Atk = int(self.Atk) + 1
            self.Def = int(self.Def * self.level) + 1

            if self.Def > max_def_stat:
                self.Vitality = self.Vitality + (self.Def / 1000000000)
                self.Def = int(self.Def / 100)

            self.gain_crit_damage((0.0002 * self.level))
            

        if themed_names[2] in self.PlayerName.lower():
            self.MHP = int(self.MHP * 15)
            self.Atk = int(self.Atk * 8)
            self.CritRate = self.CritRate / 1000

        if themed_names[3] in self.PlayerName.lower():
            self.Atk = int(self.Atk * 1.5)
            self.Def = int(self.Def * 1.5)
            self.CritDamageMod = self.CritDamageMod * ((0.005 * self.level) + 1)
            self.DodgeOdds = self.DodgeOdds / 1000

        if themed_names[4] in self.PlayerName.lower():
            self.Atk = int(self.Atk * 1.5)
            self.Def = int(self.Def * 0.5) + 1
            self.gain_crit_rate(1)
            self.CritDamageMod = self.CritDamageMod * ((0.035 * self.level) + 1)

        if themed_names[5] in self.PlayerName.lower():
            self.Vitality = self.Vitality * (0.0002 * self.level)

        if themed_names[6] in self.PlayerName.lower():
            tempname = self.PlayerName
            self.load_mimic()
            self.MHP = int(self.MHP / ((10000 / self.level) + 1))
            self.Atk = int(self.Atk / 5)
            self.Def = int(self.Def / 4)
            self.Regain = self.Regain / 5
            self.Vitality = self.Vitality / 4
            self.PlayerName = tempname
            self.set_photo("Player".lower())

        if themed_names[7] in self.PlayerName.lower():
            self.MHP = int(self.MHP * 150)

        if themed_names[8] in self.PlayerName.lower():
            self.Regain = self.Regain * (0.02 * self.level)

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
            self.MHP = int(self.MHP * 250)
            self.Atk = int(self.Atk * 2)
            self.CritDamageMod = self.CritDamageMod * 0.8

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
        max_crit_rate = 5

        while self.DodgeOdds > (max_dodgeodds + 0.01):
            self.Def = self.Def + 1
            self.gain_crit_rate(0.0001)
            self.DodgeOdds = self.DodgeOdds - 0.001

        if self.DodgeOdds > max_dodgeodds:
            self.DodgeOdds = max_dodgeodds

        while self.CritRate > (max_crit_rate + 0.01):
            self.gain_crit_damage(0.001)
            self.CritRate = self.CritRate - 0.0001

        if self.CritRate > max_crit_rate:
            self.CritRate = max_crit_rate

        if self.Vitality < 0.9:
            print("Warning Vitality is low... numbers are wrong?")

        if self.Vitality < 0.1:
            print("Warning Vitality is way too low... fixing...")
            self.Vitality = 1

    def level_up(self, mod=1):
        """
        Levels up the player by 1 and allows the user to choose which stat to increase.
        """
        from gamestates import display_stats_menu
        self.level += 1

        mod_fixed = (mod * 0.15) + 1
        int_mod = int(mod_fixed)

        hp_up: int = random.randint(25 * self.level, 55 * self.level) * int_mod
        def_up: int = random.randint(5 * self.level, 20 * self.level) * int_mod
        atk_up: int = random.randint(15 * self.level, 35 * self.level) * int_mod
        regain_up: float = random.uniform(0.001 * self.level, 0.005 * self.level) * mod_fixed
        critrate_up: float = random.uniform(0.001 * self.level, 0.0025 * self.level) * mod_fixed
        critdamage_up: float = random.uniform(0.004 * self.level, 0.008 * self.level) * mod_fixed
        dodgeodds_up: float = random.uniform(0.0002 * self.level, 0.0004 * self.level) * mod_fixed
        vitality_up: float = random.uniform(0.00000001 * self.level, 0.00000002 * self.level) * max((mod_fixed / 100), 1)

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
            self.gain_crit_rate(critrate_up)
        elif choice == 7:
            self.gain_crit_damage(critdamage_up)
        elif choice == 8:
            self.DodgeOdds += dodgeodds_up
        elif choice == 9:
            self.MHP += int(hp_up / 5)
            self.HP += int(hp_up / 5)
            self.Def += int(def_up / 5)
            self.Atk += int(atk_up / 5)
            self.Regain += regain_up / 5
            self.gain_crit_rate(critrate_up / 5)
            self.gain_crit_damage(critdamage_up / 5)
            self.DodgeOdds += dodgeodds_up / 5
        
        if self.level > 300:
            self.Vitality += vitality_up

        self.check_stats()

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
    
    def set_level(self, level):
        self.level = level
        self.MHP: int = random.randint(5 * self.level, 12 * self.level) + 100
        self.HP: int = self.MHP
        self.Def: int = self.Def + int(self.MHP * (0.000005 * self.level)) + 50
        self.Atk: int = random.randint(5 * self.level, 15 * self.level) + (self.level * 2)
        self.Regain: float = random.uniform(0.0001 * self.level, (self.level * 0.002)) + (self.level * 0.004)
        self.CritRate: float = random.uniform(0.001 * self.level, (self.level * 0.002)) + (self.level * 0.001)
        self.CritDamageMod: float = 2 + (self.level * 0.0025)
        self.DodgeOdds: float = 0.03 + (self.level * 0.0001)

        if level > 50:
            self.MHP = self.MHP + (2 * level)
            self.Atk = self.Atk + (20 * level)
            self.Vitality = self.Vitality + (0.0003 * level)
            
            # Apply bonus every xyz levels past 10
            xyz = 10
            bonus_levels = (level - 50) // xyz
            self.MHP = self.MHP + (1000 * bonus_levels)
            self.Atk = self.Atk + (20 * bonus_levels)
            self.Def = self.Def - (12 * bonus_levels)
            self.Vitality = self.Vitality + (0.0001 * (bonus_levels * level))

        if level > 100:
            self.MHP = self.MHP + (4 * level)
            self.Atk = self.Atk + (25 * level)
            self.Def = self.Def + (5 * level)
            self.Vitality = self.Vitality + (0.0002 * level)
            self.CritRate = self.CritRate + 0.01

        if level > 150:
            self.MHP = self.MHP + (8 * level)
            self.Atk = self.Atk + (30 * level)
            self.Def = self.Def + (15 * level)
            self.Vitality = self.Vitality + (0.0003 * level)
            self.CritRate = self.CritRate + 0.05

        if level > 200:
            self.MHP = self.MHP + (16 * level)
            self.Atk = self.Atk + (40 * level)
            self.Def = self.Def + (30 * level)
            self.Vitality = self.Vitality + (0.0004 * level)
            self.CritRate = self.CritRate + 0.1

        self.check_stats()
        self.check_name_mod()

        top_level = 500
        top_level_full = 1000

        self.MHP = self.MHP + int(100 * (level / top_level))
        self.Atk = self.Atk + int(50 * (level / top_level))
        self.Def = self.Def + int(60 * (level / top_level))
        self.gain_crit_rate(0.002 * (level / top_level_full))
        self.Vitality = max((self.Vitality * (level / (top_level_full * 1))), 0.75)
        self.DodgeOdds = self.DodgeOdds * (level / top_level_full)

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