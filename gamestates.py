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
    player = Player("Player")

    player.load()
    player.set_photo("Player".lower())

    if player.level < 5:
        player.load_past_lives()

    player_photo_preloaded = os.path.join(player.photo)
    player_profile_pic = pygame.image.load(player_photo_preloaded)

    while True:

        player.Bleed = 0
        player.DamageDealt = 0
        player.DamageTaken = 0

        if level < player.level:
            level = player.level + 1
        
        themed_name = random.choice(themed_names).capitalize()
        themed_title = random.choice(themed_ajt).capitalize()

        foe_pre_name = f"{themed_title} {themed_name}"

        foe = Player(f"{foe_pre_name}")
        foe.set_photo(themed_name.lower())
        foe.set_level(level)

        foe_photo_preloaded = os.path.join(foe.photo)
        foe_profile_pic = pygame.image.load(foe_photo_preloaded)
        foe_profile_pic = pygame.transform.flip(foe_profile_pic, True, False)
        foe_profile_pic = pygame.transform.scale(foe_profile_pic, (photo_size, photo_size))

        # Initialize item positions and velocity for tossing
        for item in player.Inv:
            item.position = (SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2)
            item.velocity = 0
            item.arc_offset = 0

        foe.update_inv(get_weapon(get_random_weapon()), True)

        for item in foe.Inv:
            item.position = (SCREEN_WIDTH * 5 // 6, SCREEN_HEIGHT // 2)
            item.velocity = 0
            item.arc_offset = 0

        # Index to track the current item being tossed
        player_item_index = 0
        foe_item_index = 0

        # Initialize timers for both players before the main loop
        last_player_toss = pygame.time.get_ticks() 
        last_foe_toss = pygame.time.get_ticks()
        player_last_hp_update = pygame.time.get_ticks()
        foe_last_hp_update = pygame.time.get_ticks()
        toss_interval = 1000 / 60  # 1 second in milliseconds


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
                    print("oops you died")
                    player.HP = 0

            enrage_timer.check_timeout()
            
            fps = clock.get_fps()

            enrage_mod = enrage_timer.get_timeout_duration()
            level_base_enrage_mod = (level / max(level / 1000, 1))
            player_base_enrage_mod = (enrage_mod * (level_base_enrage_mod * player.Vitality * max(player.DodgeOdds / 10, 1)))
            foe_base_enrage_mod = (enrage_mod * (level_base_enrage_mod * foe.Vitality * max(foe.DodgeOdds / 10, 1)))

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

            # Define movement speed for items (adjust this for faster/slower movement)
            toss_velocity = max(80, 2 * min(bleed_mod, 75))

            current_time = pygame.time.get_ticks()
            if current_time - player_last_hp_update >= (1000 / max(player.Vitality, 1)):
                player.HP = player.HP + int(player.Regain * (player.Vitality ** 5)) - int((player.Bleed * bleed_mod) / player.Def)
                player_last_hp_update = current_time

            if current_time - foe_last_hp_update >= (1000 / max(foe.Vitality, 1)):
                foe.HP = foe.HP + int(foe.Regain * (foe.Vitality ** 5)) - int((foe.Bleed * bleed_mod) / foe.Def)
                foe_last_hp_update = current_time
    
            current_time = pygame.time.get_ticks()

            if player.HP < 1:
                log(red, "you lose... restart game to load a new buffed save file")
                player.save_past_life()
                pygame.quit()
                input("Press enter to exit: ")
                exit()
            elif player.HP > player.MHP:
                player.HP = player.MHP

            if foe.HP < 1:
                log(white, "Saving Data")
                level = level + 1
                
                if bleed_mod < 100:
                    player.RushStat += 1
                    for multiplier in range(player.RushStat):
                        level = level + 1
                        player.level_up(mod=bleed_mod)
                else:
                    player.RushStat = 0

                log(white, "The foe has leveled up")
                player.level_up(mod=bleed_mod)
                player.save()
                break
            elif foe.HP > foe.MHP:
                foe.HP = foe.MHP

            # Toss one item from the player to the foe every 1 second
            if current_time - last_player_toss >= toss_interval:
                if player_item_index >= len(player.Inv):
                    player_item_index = 0  # Loop over items

                current_item = player.Inv[player_item_index]
                if current_item.velocity == 0:
                    # Set initial velocity and a random arc offset
                    current_item.velocity = toss_velocity
                    current_item.arc_offset = random.randint(-15, 15)  # Random arc up or down

                end_pos = (SCREEN_WIDTH * 5 // 6, SCREEN_HEIGHT // 2)
                current_item.position = move_towards_with_arc(current_item.position, end_pos, current_item.velocity, current_item.arc_offset)

                # Check if the item has reached the foe's text
                foe_rect = font.render(foe.PlayerName, True, (255, 255, 255)).get_rect(center=(SCREEN_WIDTH * 5 // 6, SCREEN_HEIGHT // 2))
                if foe_rect.collidepoint(current_item.position):
                    take_damage(player, foe, [bleed_mod, enrage_timer, current_item], def_mod)

                    current_item.velocity = 0  # Reset velocity after hit
                    current_item.position = (SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2)
                    player_item_index += 1  # Move to the next itemc

                # Reset the toss timer after an item is tossed
                del current_item
                last_player_toss = current_time 


            # Toss one item from the foe to the player every 1 second
            if current_time - last_foe_toss >= toss_interval: 
                if foe_item_index >= len(foe.Inv):
                    foe_item_index = 0  # Loop over items

                current_item = foe.Inv[foe_item_index]
                if current_item.velocity == 0:
                    # Set initial velocity and a random arc offset
                    current_item.velocity = toss_velocity
                    current_item.arc_offset = random.randint(-15, 15)  # Random arc up or down

                end_pos = (SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2)
                current_item.position = move_towards_with_arc(current_item.position, end_pos, current_item.velocity, current_item.arc_offset)

                # Check if the item has reached the player's text
                player_rect = font.render(player.PlayerName, True, (255, 255, 255)).get_rect(center=(SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2))
                if player_rect.collidepoint(current_item.position):
                    take_damage(foe, player, [bleed_mod, enrage_timer, current_item], def_mod)

                    current_item.velocity = 0  # Reset velocity after hit
                    current_item.position = (SCREEN_WIDTH * 5 // 6, SCREEN_HEIGHT // 2)
                    foe_item_index += 1  # Move to the next item

                # Reset the toss timer after an item is tossed
                del current_item
                last_foe_toss = current_time


            # Render the screen
            screen.fill((0, 0, 0))
            screen.blit(background_image, (0, 0))

            render_player_obj(pygame, player, player_profile_pic, screen, enrage_timer, def_mod, bleed_mod, (50, 585), (photo_size / 2, photo_size / 2), True)
            render_player_obj(pygame, foe, foe_profile_pic, screen, enrage_timer, def_mod, bleed_mod, (50 * 4, 585), (photo_size / 2, photo_size / 2), True)

            foe_stat_data = [
                ("Stats of:", foe.PlayerName),
                ("Level:", foe.level),
                ("Max HP:", foe.MHP),
                ("Atk:", int(foe.Atk)),
                ("Def:", int(foe.Def / def_mod)),
                ("Crit Rate:", f"{(foe.CritRate * 100):.1f}%"),
                ("Crit Damage Mod:", f"{(foe.CritDamageMod):.2f}x"),
                ("HP Regain:", f"{(foe.Regain * 100):.0f}"),
            ]

            if len(foe.Items) > 0:
                foe_stat_data.append(("Blessings:", f"{len(foe.Items)}"))

            if foe.Vitality / def_mod > 1.5:
                foe_stat_data.append(("Vitality:", f"{(foe.Vitality / def_mod):.2f}x"))

            if (foe.DodgeOdds * 100) / bleed_mod > 1:
                foe_stat_data.append(("Dodge Odds:", f"{((foe.DodgeOdds * 100) / bleed_mod):.2f}%"))

            if foe.Bleed != 0:
                foe_stat_data.append(("Bleed:", f"{foe.Bleed:.1f}x"))

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
                
            if enrage_timer.timed_out:
                fps_stat = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
                enrage_timer_stat = font.render(f"Enrage: {(enrage_mod + enrage_timer.timeout_seconds):.1f}", True, (255, 255, 255))
                fps_rect = fps_stat.get_rect(center=((SCREEN_WIDTH // 8) + 600, (SCREEN_HEIGHT // 2) - 400))
                enrage_timer_rect = fps_stat.get_rect(center=((SCREEN_WIDTH // 8) + 600, (SCREEN_HEIGHT // 2) - 350))
                screen.blit(fps_stat, fps_rect)
                screen.blit(enrage_timer_stat, enrage_timer_rect)
            else:
                fps_stat = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
                fps_rect = fps_stat.get_rect(center=((SCREEN_WIDTH // 8) + 600, (SCREEN_HEIGHT // 2) - 400))
                screen.blit(fps_stat, fps_rect)

            # Draw the foe's name
            foe_text = font.render(foe.PlayerName, True, (255, 255, 255))
            foe_rect = foe_text.get_rect(center=(SCREEN_WIDTH * 5 // 6, SCREEN_HEIGHT // 2))
            screen.blit(foe_text, foe_rect)

            # Draw the foe's HP bar
            foe_hp_percent = foe.HP / foe.MHP * 100
            foe_hp_bar = pygame.Rect(foe_rect.x, foe_rect.y + 60, foe_hp_percent * 4, 5)
            pygame.draw.rect(screen, (255, 0, 0), foe_hp_bar)

            # Draw the foe's profile picture
            if foe_hp_percent < 75:
                foe_profile_pic.set_alpha(int(255 * foe_hp_percent / 75))

            screen.blit(foe_profile_pic, (foe_rect.x + 0, foe_rect.y + 85))

            # Draw the current tossed items
            if player_item_index < len(player.Inv):
                current_item = player.Inv[player_item_index]
                item_text = font.render(current_item.game_obj, True, (255, 255, 255))
                item_rect = item_text.get_rect(center=current_item.position)
                screen.blit(item_text, item_rect)

            if foe_item_index < len(foe.Inv):
                current_item = foe.Inv[foe_item_index]
                item_text = font.render(current_item.game_obj, True, (255, 255, 255))
                item_rect = item_text.get_rect(center=current_item.position)
                screen.blit(item_text, item_rect)

            # Flip the display
            pygame.display.flip()