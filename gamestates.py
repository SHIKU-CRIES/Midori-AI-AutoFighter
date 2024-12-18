import os
import sys
import pygame
import random

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

def display_stats_menu(hp_up, def_up, atk_up, regain_up, critrate_up, critdamage_up, dodgeodds_up, damage_taken, damage_dealt, items):
    screen = temp_screen.screen
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 25)

    # Create the menu items
    menu_items = [
        ('HP', hp_up),
        ('Def', def_up),
        ('Atk', atk_up),
        ('Regain', regain_up),
        ('CritRate', critrate_up),
        ('CritDamageMod', critdamage_up),
        ('DodgeOdds', dodgeodds_up),
        ('Random Blessing Or Upgrade Blessing', 1)
    ]

    menu_stats = [
        ('Damage Taken:', damage_taken),
        ('Damage Dealt:', damage_dealt)
    ]

    for item in items:
        menu_stats.append((item.name, f"{item.power:.1f}"))

    # Button dimensions and spacing
    button_width = 600
    button_height = 40
    button_margin = 10

    # Create button rectangles
    buttons = []
    for i, (text, value) in enumerate(menu_items):
        button_x = 10
        button_y = 20 + (i * (button_height + button_margin))
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        buttons.append((button_rect, i + 1))

    stats = []
    for i, (text, value) in enumerate(menu_stats):
        text_x = 650
        text_y = 20 + (i * (button_height + button_margin))
        text_rect = pygame.Rect(text_x, text_y, button_width, button_height)
        stats.append((text_rect, i + 1))

    # Add Autopick button
    autopick_button_rect = pygame.Rect(button_x, 20 + len(menu_items) * (button_height + button_margin),
                                       button_width, button_height)

    # Handle user input
    while True:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse click
                    for button_rect, value in buttons:
                        if button_rect.collidepoint(event.pos):
                            return value
                    if autopick_button_rect.collidepoint(event.pos):
                        with open("auto.pick", 'w') as file:
                            file.write("hi")
                        return 10

        # Draw menu items and buttons
        screen.fill((0, 0, 0))  # Clear the screen

        for i, ((text, value), (button_rect, _)) in enumerate(zip(menu_items, buttons)):
            # Draw button background
            pygame.draw.rect(screen, (100, 100, 100), button_rect)

            # Draw button text
            text_surface = font.render(f'{i+1}. {text} (+{value})', True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)

        for i, ((text, value), (button_rect, _)) in enumerate(zip(menu_stats, stats)):
            # Draw button background
            pygame.draw.rect(screen, (100, 100, 100), button_rect)

            # Draw button text
            text_surface = font.render(f'{i+1}. {text} (+{value})', True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)

        # Draw Autopick button
        pygame.draw.rect(screen, (100, 100, 100), autopick_button_rect)
        autopick_text = "Autopick"
        text_surface = font.render(autopick_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=autopick_button_rect.center)
        screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(10)

# Helper function to move an item towards a target, considering velocity
def move_towards_with_arc(current_pos, target_pos, velocity, arc_offset):
    cx, cy = current_pos
    tx, ty = target_pos
    dx, dy = tx - cx, ty - cy

    # Calculate the distance to the target
    dist = (dx**2 + dy**2) ** 0.5

    # If the item is already at the target, return the target position
    if dist == 0:
        return tx, ty

    # Calculate the step size in the x and y directions
    step_x = velocity * dx / dist
    step_y = velocity * (dy + arc_offset) / dist

    # If the item is close enough to the target, move it directly to the target
    if dist < 15:
        return tx, ty

    # Otherwise, move the item towards the target with the calculated step size
    return cx + step_x, cy + step_y


def log(color, text):
    print(color + text + Style.RESET_ALL)

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

    player = Player("Player")

    player.load()
    player.set_photo("Player".lower())

    if player.level < 5:
        player.load_past_lives()

    starting_level = player.level

    player.photodata = pygame.image.load(os.path.join(player.photo))

    playerlist.append(player)
        
    for i in range(3):
        themed_name = random.choice(themed_names).capitalize()

        player = Player(f"{themed_name}")
        player.set_photo(themed_name.lower())
        player.set_level(starting_level)

        player.photodata = pygame.image.load(os.path.join(player.photo))
        playerlist.append(player)

    while True:
        
        foelist: list[Player] = []

        for player in playerlist:
            player.Bleed = 0
            player.DamageDealt = 0
            player.DamageTaken = 0

        if level < player.level:
            level = player.level + 1
        
        for i in range(5):
            themed_name = random.choice(themed_names).capitalize()
            themed_title = random.choice(themed_ajt).capitalize()

            foe_pre_name = f"{themed_title} {themed_name}"

            foe = Player(f"{foe_pre_name}")
            foe.set_photo(themed_name.lower())
            foe.set_level(level)

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
            level_base_enrage_mod = (level / max(level / 1000, 1))
            player_base_enrage_mod = (enrage_mod * level_base_enrage_mod)
            foe_base_enrage_mod = (enrage_mod * level_base_enrage_mod)

            if enrage_mod > 10:
                buffed_starter = ((enrage_mod - 10) * 0.000000004) + ((enrage_mod - 5) * 0.000000002)
                bleed_mod = ((0.00000002 + buffed_starter) * (player_base_enrage_mod * foe_base_enrage_mod)) + 1
            elif enrage_mod > 5:
                buffed_starter = ((enrage_mod - 5) * 0.000000002)
                bleed_mod = ((0.00000002 + buffed_starter) * (player_base_enrage_mod * foe_base_enrage_mod)) + 1
            else:
                bleed_mod = (0.00000002 * (player_base_enrage_mod * foe_base_enrage_mod)) + 1

            def_mod = max(1, (bleed_mod * 0.05))

            if bleed_mod > 15:
                def_mod = max(1, (bleed_mod * 0.02) + (bleed_mod * 0.02) + (bleed_mod * 0.01))
            
            if bleed_mod > 35:
                def_mod = max(1, (bleed_mod * 0.04) + (bleed_mod * 0.04) + (bleed_mod * 0.02))

            fps_cap = 20
            dt = clock.tick(fps_cap) / 1000
    

            # Render the screen
            screen.fill((0, 0, 0))
            screen.blit(background_image, (0, 0))

            foe_bottom = 100
            player_bottom = 625
            item_total_size = photo_size / 2
            size = (item_total_size, item_total_size)

            if len(playerlist) > 0:
                for i, testplayer in enumerate(playerlist):
                    item_total_position = ((25 * i) + (50 + (item_total_size * i)), player_bottom)
                    render_player_obj(pygame, testplayer, testplayer.photodata, screen, enrage_timer, def_mod, bleed_mod, item_total_position, size, True)

                    if testplayer.HP > 0:
                        testplayer.HP = testplayer.HP + int(testplayer.Regain * (testplayer.Vitality ** 5)) - int((testplayer.Bleed * bleed_mod) / testplayer.Def)

                        if len(foelist) > 0:
                            tartget_to_damage = random.choice(foelist)
                            take_damage(tartget_to_damage, testplayer, [bleed_mod, enrage_timer], def_mod)

                            if tartget_to_damage.HP < 1:
                                foelist.remove(tartget_to_damage)
                                log(white, "Saving Data")
                                level = level + 1
                                testplayer.level_up(mod=bleed_mod)
                                testplayer.save()

                            elif tartget_to_damage.HP > tartget_to_damage.MHP:
                                tartget_to_damage.HP = tartget_to_damage.MHP

                        else:
                            if testplayer.HP < 1:
                                testplayer.save_past_life()
                                playerlist.remove(testplayer)

                            elif testplayer.HP > testplayer.MHP:
                                testplayer.HP = testplayer.MHP
            else:
                log(red, "you lose... restart game to load a new buffed save file")
                pygame.quit()
                input("Press enter to exit: ")
                exit()

            if len(foelist) > 0:
                for i, testfoe in enumerate(foelist):
                    item_total_position = ((25 * i) + (50 + (item_total_size * i)), foe_bottom)
                    render_player_obj(pygame, testfoe, testfoe.photodata, screen, enrage_timer, def_mod, bleed_mod, item_total_position, size, True)

                    testfoe.HP = testfoe.HP + int(testfoe.Regain * (testfoe.Vitality ** 5)) - int((testfoe.Bleed * bleed_mod) / testfoe.Def)

                    if len(playerlist) > 0:
                        tartget_to_damage = random.choice(playerlist)
                        take_damage(tartget_to_damage, testfoe, [bleed_mod, enrage_timer], def_mod)
            else:
                break

            pygame.display.flip()