# Party UI

The party management interface uses a unified `CharacterEditor` inside `StatTabs` for both player and non‑player characters. The editor exposes sliders for HP, Attack, Defense, Crit Rate, and Crit Damage. Player edits persist via `/player/editor` while NPC tweaks remain local for previewing.

An `UpgradePanel` sits below the editor so any character can convert upgrade items into points and spend them on specific stats using the shared `/players/<id>/upgrade` and `/players/<id>/upgrade-stat` endpoints.

`StatTabs` no longer includes the old Effects tab; all characters share the same scrollable stat view and slider controls.
