# Gameplay Overview

When I launch the web-based game the Svelte frontend shows a dark, glassy main menu rendered as a high-contrast icon grid. A slim top bar displays my small avatar, name, and pull count. A frosted panel hugs the upper-left corner with a horizontal row of **Avatar**, **Pulls**, and **Crafting** buttons, each icon perched above its label. The right side pushes a vertical stack of **Run**, **Edit Player**, **Edit Team**, **Settings**, and **Quit** further to the edge so their labels sit beside their icons. Curious, I press **Run** and a modal party picker fades in over a random backdrop. The frontend asks the backend for the full plugin roster and only shows entries I own, with my avatar pinned to the top. I can add up to four allies beneath it. After confirming, the frontend calls the Quart backend to start a new run, returning a run ID and a generated map that the backend writes to the encrypted `save.db` so progress survives restarts.

A simple row of room buttons appears, one for each node on the map. Tapping a button now calls the Quart endpoint for that room and shows a view with foes arrayed across the top and my party on the bottom, each ally tagged with a small ultimate circle.

On a desktop monitor the party picker, player editor, and a stats panel flank the main menu. Tablets show the menu beside the party picker, while phones limit the view to one menu at a time so navigation stays simple.

Battle rooms will have my team automatically trading blows with enemies while damage numbers and status icons pop up. Shop rooms will display items with prices and star ratings, letting me spend gold or reroll the stock. Rest rooms will offer a calm break where I can heal or trade items before heading back to the map.

Along the way I'll collect cards and relics. Cards will give small stat boosts or special perks, while relics provide stronger passive effects that persist through the run.

Clearing room after room will eventually bring me to a boss icon. Beating the boss finishes the floor and I'll return to the map or the main menu. Between runs I can roll the gacha for new characters and tweak my player appearance.

This document reflects how the game currently plays and should be kept up to date as features evolve.
