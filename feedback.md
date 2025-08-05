## UI Bug Feedback: Endless Autofighter

This feedback is based on the attached screenshots of the game menus.

### Main Menu
The main menu appears to render correctly, with all buttons and text visible and properly aligned.

### Edit Player Menu (Buggy)
In the Edit Player menu (see second screenshot), the UI is severely broken:
- The interface is excessively zoomed in.
- Text and buttons overlap, making the menu unreadable.
- Layout is distorted, with elements rendered far larger than intended.

### Settings Menu (Buggy)
In the Settings menu (see third screenshot), similar issues are present:
- UI elements are scaled incorrectly.
- Text and buttons overlap and are unreadable.
- The layout is completely broken, with elements stacked on top of each other.

#### Possible Causes
These issues may be related to:
- UI scaling logic
- Font size settings
- Window resizing or DPI handling


---

#### Files to Review and Debugging Suggestions

Based on the project structure, the following files are likely responsible for the UI scaling and rendering logic in the Edit Player and Settings menus:

- `main.py`: Entry point for the game, may initialize window size, scaling, or global UI parameters.

Additionally, review the following test files to ensure UI layout issues are covered:
- `tests/test_menu.py`
- `tests/test_player_creator.py`
- `tests/test_stat_screen.py`

If these tests do not catch scaling or rendering bugs, consider expanding them to include UI layout validation.

Also, check for any global configuration files or constants that affect font size, DPI, or window scaling. These may be set in `main.py` or in a shared config module.

#### Scale Parameter Analysis and Recommendation

Upon reviewing the code, there is a notable difference in the `scale` parameter used for UI elements:

- In `autofighter/menu.py` (main menu), some elements use `scale=0.1`.
- In `autofighter/menu.py` (other menus, e.g., options/settings), and in `autofighter/player_creator.py` (edit player menu), elements use `scale=0.5`.

This inconsistency likely causes the main menu to render correctly while the Edit Player and Settings menus appear excessively zoomed in and broken.

**Actionable Suggestions:**
- Audit all `scale` parameters in `autofighter/menu.py` and `autofighter/player_creator.py`.
- Standardize scale usage across all menus to ensure consistent UI appearance.
- Consider defining a global scale constant or function to manage UI scaling, making future maintenance easier and preventing similar bugs.

Consistent scaling logic will help resolve the current UI issues and improve the overall user experience.
