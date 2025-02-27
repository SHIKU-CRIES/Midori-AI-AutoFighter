import os
import sys
import pygame
import random
import importlib

from screendata import Screen

from weapons import get_weapon
from weapons import get_random_weapon

from timerhelper import timmer

from damagestate import take_damage

from load_photos import set_bg_photo
from load_photos import set_bg_music
from load_photos import resource_path

from themedstuff import themed_ajt
from themedstuff import themed_names

from typing import Tuple

from colorama import Fore, Style
    
red = Fore.RED
green = Fore.GREEN
blue = Fore.BLUE
white = Fore.WHITE
yellow = Fore.YELLOW

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

photo_size = 128 * 3

enrage_timer = timmer()
temp_screen = Screen(SCREEN_WIDTH, SCREEN_HEIGHT)

def log(color, text):
    print(color + text + Style.RESET_ALL)
    return text

def debug_log(filename, text):
    with open(filename, "a") as f:
        f.write(f"\n{text}")
    
    return text

def kill_person(dead, killer):
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"{killer.PlayerName} killed {dead.PlayerName}, Below are stats for both...")

    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Dead Person")

    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Name: {dead.PlayerName}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Level: {dead.level}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"MHP: {dead.MHP}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"HP: {dead.HP}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Defense: {dead.Def}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Attack: {dead.Atk}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Regain: {dead.Regain}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"True Vitality: {dead.Vitality}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Crit Rate: {dead.CritRate}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Crit Damage Modifier: {dead.CritDamageMod}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Dodge Odds: {dead.DodgeOdds}")
    
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Killer")

    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Name: {killer.PlayerName}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Level: {killer.level}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"MHP: {killer.MHP}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"HP: {killer.HP}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Defense: {killer.Def}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Attack: {killer.Atk}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Regain: {killer.Regain}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"True Vitality: {killer.Vitality}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Crit Rate: {killer.CritRate}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Crit Damage Modifier: {killer.CritDamageMod}")
    debug_log(os.path.join("logs", f"{dead.PlayerName.lower()}.txt"), f"Dodge Odds: {killer.DodgeOdds}")

def main(level):
    from player import Player
    from player import render_player_obj

    pygame.init()

    # Create the screen
    screen = temp_screen.screen
    icon = pygame.image.load(resource_path(os.path.join("photos", f"midoriai-logo.png")))
    pygame.display.set_icon(icon)
    
    pygame.display.set_caption("Midori AI Auto Fighter", "Welcome to the fighting zone!")

    # Create a clock
    clock = pygame.time.Clock()

    # Create a font object
    font = pygame.font.SysFont('Arial', 44)

    # Set the running flag to True
    running = True
    foes_killed = 1

    background_file_name = set_bg_photo()
    background_image = pygame.image.load(background_file_name)
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    background_image.set_alpha(128)

    pygame.mixer.music.set_volume(0.05 / 2)
    music = pygame.mixer.music.load(set_bg_music())
    pygame.mixer.music.play(-1)  # -1 means loop the music indefinitely

    screen.fill((0, 0, 0))
    screen.blit(background_image, (0, 0))

    pygame.display.flip()

    # Create the player and foe objects
    playerlist: list[Player] = []
    temp_themed_names: list[str] = []

    for item in themed_names:
        if "mimic".lower() in item.lower():
            continue
        else:
            temp_themed_names.append(item)

    player = Player("Player")

    player.load()
    player.set_photo("Player".lower())

    if player.level < 5:
        player.load_past_lives()

    player.photodata = pygame.image.load(os.path.join(player.photo))

    playerlist.append(player)
        
    for i in range(4):
        if random.random() < 0.7:
            themed_name = temp_themed_names[0].capitalize()
        else:
            themed_name = random.choice(temp_themed_names[1:]).capitalize()

        temp_themed_names.remove(themed_name.lower())

        player = Player(f"{themed_name}")
        player.load()
        player.set_photo(themed_name.lower())

        if player.level < 5:
            player.load_past_lives()

        player.photodata = pygame.image.load(os.path.join(player.photo))
        playerlist.append(player)

    while True:

        level_sum = 0
        max_player_level = 0
        foelist: list[Player] = []

        for player in playerlist:
            if player.level > max_player_level:
                max_player_level = player.level

        for player in playerlist:
            player.Bleed *= 0.65
            player.DamageDealt = 0
            player.DamageTaken = 0

            level_sum += player.level

            while player.level < max_player_level:
                player.level_up(player.Kills * 2)

        average_level = round((level_sum + (foes_killed * 2)) / len(playerlist))
        level = average_level

        if level < 250:
            number_of_foes = 6
        elif level < 500:
            number_of_foes = 5
        elif level < 1000:
            number_of_foes = 5
        else:
            number_of_foes = 5
        
        foes_killed += number_of_foes

        temp_foe_themed_names: list[str] = []

        for item in themed_names:
            temp_foe_themed_names.append(item)

        if level < 1800:
            temp_foe_themed_names.remove("Carly".lower())

        if level < 3000:
            temp_foe_themed_names.remove("Luna".lower())

        for i in range(number_of_foes):
            themed_name = random.choice(temp_foe_themed_names).capitalize()

            temp_foe_themed_names.remove(themed_name.lower())

            themed_title = random.choice(themed_ajt).capitalize()

            foe_pre_name = f"{themed_title} {themed_name}"

            foe = Player(f"{foe_pre_name}")
            foe.set_photo(themed_name.lower())
            foe.set_level(random.randint(max(level - 10, 1), level + 10))

            foe.photodata = pygame.image.load(os.path.join(foe.photo))
            foe.photodata = pygame.transform.flip(foe.photodata, True, False)
            foe.photodata = pygame.transform.scale(foe.photodata, (photo_size, photo_size))

            foe.update_inv(get_weapon(get_random_weapon()), True)

            foelist.append(foe)

        # heal the player
        player.HP = player.MHP

        enrage_timer.reset()
        enrage_timer.start()

        # Main game loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_d: 
                    for player in playerlist:
                        player.HP = 0

            enrage_timer.check_timeout()
            
            fps = clock.get_fps()

            enrage_mod = enrage_timer.get_timeout_duration()
            level_base_enrage_mod = (level / max(level / 1000, 15))
            player_base_enrage_mod = (enrage_mod * level_base_enrage_mod)
            foe_base_enrage_mod = (enrage_mod * level_base_enrage_mod)

            if enrage_mod > 10:
                buffed_starter = ((enrage_mod - 10) * 0.00000004) + ((enrage_mod - 5) * 0.00000002)
                bleed_mod = ((0.0000002 + buffed_starter) * (player_base_enrage_mod * foe_base_enrage_mod)) + 1
            elif enrage_mod > 5:
                buffed_starter = ((enrage_mod - 5) * 0.00000002)
                bleed_mod = ((0.0000002 + buffed_starter) * (player_base_enrage_mod * foe_base_enrage_mod)) + 1
            else:
                bleed_mod = (0.0000002 * (player_base_enrage_mod * foe_base_enrage_mod)) + 1

            def_mod = max(1, (bleed_mod * 0.05))

            if bleed_mod > 15:
                def_mod = max(1, (bleed_mod * 0.02) + (bleed_mod * 0.02) + (bleed_mod * 0.01))
            
            if bleed_mod > 35:
                def_mod = max(1, (bleed_mod * 0.04) + (bleed_mod * 0.04) + (bleed_mod * 0.02))

            fps_cap = 35
            dt = clock.tick(fps_cap) / 1000
    

            # Render the screen
            screen.fill((0, 0, 0))
            screen.blit(background_image, (0, 0))

            foe_bottom = 250
            player_bottom = 625
            item_total_size = photo_size - (photo_size / 4)
            size = (item_total_size, item_total_size)

            if len(foelist) > 0:
                foe_stat_data = [
                    ("Stats of:", foelist[0].PlayerName),
                    ("Level:", foelist[0].level),
                    ("Max HP:", foelist[0].MHP),
                    ("Atk:", int(foelist[0].Atk)),
                    ("Def:", int(foelist[0].Def / def_mod)),
                    ("Crit Rate:", f"{(foelist[0].CritRate * 100):.1f}%"),
                    ("Crit Damage Mod:", f"{(foelist[0].CritDamageMod):.2f}x"),
                    ("HP Regain:", f"{(foelist[0].Regain * 100):.0f}"),
                ]

                if len(foelist[0].Items) > 0:
                    foe_stat_data.append(("Blessings:", f"{len(foelist[0].Items)}"))

                if foelist[0].Vitality / def_mod > 1.5:
                    foe_stat_data.append(("Vitality:", f"{(foelist[0].Vitality / def_mod):.2f}x"))

                if (foelist[0].DodgeOdds * 100) / bleed_mod > 1:
                    foe_stat_data.append(("Dodge Odds:", f"{((foelist[0].DodgeOdds * 100) / bleed_mod):.2f}%"))

                if foelist[0].Bleed != 0:
                    foe_stat_data.append(("Bleed:", f"{foelist[0].Bleed:.1f}x"))

                # Foe stats drawing
                foe_x_offset = SCREEN_WIDTH - (SCREEN_WIDTH // 8) + 170
                foe_y_offset = (SCREEN_HEIGHT // 2) - 425 

                foe_num_stats = len(foe_stat_data)

                foe_spacing_moded = 55 - (foe_num_stats * 2)

                foe_font_size = max(16, 54 - 2 * foe_num_stats) 
                foe_stats_font = pygame.font.SysFont('Arial', foe_font_size)

                try:
                    for i, (stat_name, stat_value) in enumerate(foe_stat_data):
                        stat_text = foe_stats_font.render(f"{stat_name} {stat_value}", True, (255, 255, 255))
                        stat_rect = stat_text.get_rect(topright=(foe_x_offset, foe_y_offset + i * foe_spacing_moded))
                        screen.blit(stat_text, stat_rect)
                except Exception as error:
                    print(f"Could not render foe stats due to {str(error)}")

                for i, person in enumerate(foelist):
                    item_total_position = ((25 * i) + (50 + (item_total_size * i)), foe_bottom)
                    render_player_obj(pygame, person, person.photodata, screen, enrage_timer, def_mod, bleed_mod, item_total_position, size, True)

                    if person.Bleed > person.MHP * 0.001:
                        person.Bleed = max(person.Bleed - (person.Regain * 25), person.MHP * 0.001)
                    else:
                        person.Bleed = max(person.Bleed - (person.Regain * 5), 0)

                    person.HP = min(person.MHP, person.HP + int(person.Regain * person.Vitality) - int(person.Bleed  / person.Vitality))

                    if len(playerlist) > 0:
                        tartget_to_damage = random.choice(playerlist)
                        take_damage(tartget_to_damage, person, [bleed_mod, enrage_timer], def_mod)

                        if tartget_to_damage.HP < 1:
                            tartget_to_damage.save_past_life()
                            kill_person(tartget_to_damage, person)
                            playerlist.remove(tartget_to_damage)
            else:
                break

            if len(playerlist) > 0:
                for i, person in enumerate(playerlist):

                    item_total_position = ((25 * i) + (50 + (item_total_size * i)), player_bottom)
                    render_player_obj(pygame, person, person.photodata, screen, enrage_timer, def_mod, bleed_mod, item_total_position, size, True)
                
                    if bleed_mod > 100:
                        person.RushStat = 0

                    if person.HP > 0:
                        if person.Bleed > person.MHP * 0.001:
                            person.Bleed = max(person.Bleed - (person.Regain * 25), person.MHP * 0.001)
                        else:
                            person.Bleed = max((person.Bleed - (person.Regain * 5)), 0)

                        person.HP = min(person.MHP, person.HP + int(person.Regain * person.Vitality) - int(person.Bleed / person.Vitality))

                        if len(foelist) > 0:
                            tartget_to_damage = random.choice(foelist)
                            take_damage(tartget_to_damage, person, [bleed_mod, enrage_timer], def_mod)

                            if tartget_to_damage.HP < 1:
                                foelist.remove(tartget_to_damage)
                                person.Kills += 1
                                log(white, "Saving Data")
                
                                if bleed_mod < 100:
                                    person.RushStat += 1
                                    person.level_up(mod=bleed_mod)
                                else:
                                    person.RushStat = 0
                                
                                person.level_up(mod=bleed_mod)
                                    
                                person.save()

                            elif tartget_to_damage.HP > tartget_to_damage.MHP:
                                tartget_to_damage.HP = tartget_to_damage.MHP

                    if person.HP > person.MHP:
                        person.HP = person.MHP
            else:
                log(red, "you lose... restart game to load a new buffed save file")
                pygame.quit()
                input("Press enter to exit: ")
                exit()
                
            if enrage_timer.timed_out:
                fps_stat = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
                enrage_timer_stat = font.render(f"Enrage: {(enrage_mod + enrage_timer.timeout_seconds):.1f} ({(bleed_mod):.2f}x)", True, (255, 255, 255))
                fps_rect = fps_stat.get_rect(center=((SCREEN_WIDTH // 8) + 600, (SCREEN_HEIGHT // 2) - 400))
                enrage_timer_rect = fps_stat.get_rect(center=((SCREEN_WIDTH // 8) + 600, (SCREEN_HEIGHT // 2) - 350))
                screen.blit(fps_stat, fps_rect)
                screen.blit(enrage_timer_stat, enrage_timer_rect)
            else:
                fps_stat = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
                fps_rect = fps_stat.get_rect(center=((SCREEN_WIDTH // 8) + 600, (SCREEN_HEIGHT // 2) - 400))
                screen.blit(fps_stat, fps_rect)

            pygame.display.flip()