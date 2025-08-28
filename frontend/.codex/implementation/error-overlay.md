# Error Overlay

`src/lib/ErrorOverlay.svelte` wraps `PopupWindow.svelte` to present API or runtime errors.
The overlay shows the error message and server traceback in a `pre` block and includes a
"Report Issue" button that opens a new GitHub issue using the `FEEDBACK_URL` constant.
It is opened via `openOverlay('error', { message, traceback })`.
