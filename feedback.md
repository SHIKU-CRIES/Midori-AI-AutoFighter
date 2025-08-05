## Endless Autofighter UI Feedback

### Main Menu Redesign (Arknights-Inspired)
- The main menu should be visually reworked to use a grid layout of large, high-contrast icons, similar to the main menu in Arknights. Key points for implementation:
  - **Grid Layout:** Use 3-4 columns of evenly spaced icons for core functions (e.g., Start, Operators, Store, Settings, Profile).
  - **Icon Design:** Each icon should be visually distinct, easily recognizable, and use minimal or no text. Consider tooltips or labels on hover/tap for accessibility.
  - **Touch/Cursor Friendly:** Icons should be large enough and spaced for easy interaction on both desktop and mobile devices.
  - **Consistent Style:** Maintain a modern, clean, and slightly futuristic aesthetic. Use a consistent color palette and icon size for harmony.
  - **Background:** Consider subtle gradients or thematic artwork in the background, as seen in Arknights, to enhance visual appeal without clutter.

### Lucide Icon Usage
- All UI components across the project should use [Lucide](https://lucide.dev/) icons for a clean, scalable, and professional look. This ensures:
  - Consistency in icon style and sizing
  - Easy customization and future updates
  - Improved readability and accessibility

### Menu Item Labeling & Accessibility
- Every menu item in all menus (not just the main menu) must have clear, visible labels. This includes:
  - Button text or tooltips for all interactive elements
  - Descriptive labels for settings, options, and actions
  - Accessibility features such as keyboard navigation and screen reader support

### Technical Issue: Panda3D Loader
- **Error:** `AttributeError: 'panda3d.core.Loader' object has no attribute 'load_model'`
- **Cause:** The method name is likely incorrect. Panda3D uses `loadModel` (camelCase), not `load_model`.
- **Action:** Update all code to use `loadModel` instead of `load_model` when loading assets with Panda3D.
- **Impact:** Fixing this will allow scenes and models to load correctly, resolving startup errors.

### General UI Issues & Recommendations
- Some menus (Edit Player, Settings) are missing labels or have placeholder content. To resolve:
  - Ensure all menus are fully labeled and functional
   - Player Menu is missing labels for the body type, hair, size.
   - Settings is missing labels for all audio stuffs
  - Replace placeholder text with meaningful labels and options
  - Review all screens for missing or unclear UI elements
  - Test on different screen sizes and DPI settings to ensure proper scaling and alignment

### Additional Suggestions
- Review UI scaling logic, font size settings, and window resizing/DPI handling to prevent layout bugs.
- Reference Arknights UI screenshots for inspiration on icon arrangement, color palette, and overall style.
- Consider user feedback and accessibility best practices for all future UI changes.

---
