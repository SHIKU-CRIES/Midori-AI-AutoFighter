# Auditor Review: Arknights Main Menu UI (Reference for Endless Autofighter)

This review is based on an exhaustive analysis of at least 10 Arknights main menu UI images from official wikis, community guides, and fan redesigns. The findings are structured for coders who cannot view the images, with actionable, multi-angle feedback.

---

## 1. Layout & Structure

- **Central Banner/Feature Area:**
  - Most menus feature a large, horizontally-oriented banner in the center or upper third, used for event promotions, news, or featured content. This area is visually dominant and often animated or highly detailed.
- **Navigation Bars:**
  - A persistent navigation bar is typically anchored at the bottom or sides, containing large, clearly labeled buttons for core sections (e.g., "Base", "Squad", "Store", "Recruit").
  - Buttons are spaced for easy tapping, with generous padding and clear separation.
- **User Info & Currency:**
  - The top edge of the screen displays user avatar, name, and in-game currencies (Originium, LMD, etc.), with icons and numeric values. These are grouped and aligned for quick scanning.
- **Quick Access/Shortcuts:**
  - Small, circular or rounded-square icons for notifications, mail, settings, and events are clustered in corners or along the sides, never overlapping main content.
- **Backgrounds:**
  - The background is often a high-quality illustration or subtle animated scene, but UI panels are semi-transparent or have a frosted-glass effect to ensure readability.
- **Grouping & Hierarchy:**
  - Related functions are grouped (e.g., all squad-related actions together), and visual hierarchy is established through size, contrast, and placement.
- **Responsiveness:**
  - UI elements scale and reposition gracefully for different device sizes, maintaining touch targets and legibility.

## 2. Color, Typography & Iconography

- **Color Palette:**
  - Dominant colors are dark (charcoal, navy, black) with high-contrast white or light text. Accent colors (orange, blue, teal, gold) are used for highlights, buttons, and notifications.
  - Event or seasonal menus may introduce unique accent colors, but core navigation remains consistent.
- **Typography:**
  - Fonts are bold, sans-serif, and highly legible. Main menu labels use large, all-caps text with strong contrast against backgrounds.
  - Secondary text (descriptions, tooltips) is smaller but still clear, often in a lighter weight or color.
- **Iconography:**
  - Icons are flat or slightly shaded, with a consistent visual language (rounded corners, minimal detail, clear silhouettes).
  - Each function (e.g., "Store", "Squad") has a unique, easily recognizable icon. Notification badges are circular and use red or orange for urgency.
- **Visual Effects:**
  - Subtle glows, drop shadows, or outlines are used to separate UI elements from busy backgrounds.
  - Animated transitions (e.g., button presses, menu slides) provide feedback but are not distracting.

## 3. Synthesis & Actionable Checklist

- **Best Practices:**
  - Use a central banner for featured content, with clear separation from navigation.
  - Anchor navigation bars with large, labeled buttons and generous spacing.
  - Group user info and currencies at the top, with clear icons and numbers.
  - Keep quick-access shortcuts in corners, never overlapping main content.
  - Use a dark, high-contrast palette with consistent accent colors.
  - Employ bold, sans-serif fonts for main labels; ensure all text is legible on dark backgrounds.
  - Maintain consistent, simple iconography with clear notification badges.
  - Ensure all UI elements are touch-friendly and responsive.
- **Pitfalls to Avoid:**
  - Avoid cluttering the main menu with too many overlapping elements or excessive animation.
  - Do not use low-contrast text or icons on busy backgrounds.
  - Avoid inconsistent icon styles or unlabeled buttons.
- **Special Notes:**
  - Event or seasonal themes may alter colors or backgrounds, but core navigation and layout remain stable.
  - Accessibility: Ensure sufficient color contrast and font size for readability.

---

**References:**
- [Arknights Wiki - User Interface](https://arknights.fandom.com/wiki/User_interface)
- [Arknights Terra Wiki - Home Screen UI](https://arknights.wiki.gg/wiki/Home_Screen/UI)
- [Game UI Database - Arknights](https://www.gameuidatabase.com/gameData.php?id=478)
- [ArtStation - Arknights UI Redesign](https://www.artstation.com/artwork/vDbzV6)
- [Reddit - New UI Themes](https://www.reddit.com/r/arknights/comments/1hmg93t/new_ui_themes/)
- [YouTube - Arknights Menu Guide & Overview](https://www.youtube.com/watch?v=QnJUHPI6wtw)
- [AppGamer - Main Menu Interface](https://www.appgamer.com/arknights/strategy-guide/main-menu-interface)
- [Steam Workshop - Arknights Main Menu Amiya](https://steamcommunity.com/sharedfiles/filedetails/?id=2466507562)
- [Reddit - Someone edited the Menu screen](https://www.reddit.com/r/arknights/comments/14ws2px/someone_edited_the_menu_screen_to_fit_the_theme/)
- [Facebook - New UI Introduction](https://www.facebook.com/ArknightsGlobal/posts/new-ui-introductionin-the-next-update-we-will-be-upgrading-the-combat-menu-into-/1707787959420415/)

---

This review is designed for coders who cannot view the images. If you need further breakdowns (e.g., per-image, per-theme), please request additional detail.