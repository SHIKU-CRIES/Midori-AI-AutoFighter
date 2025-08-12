# Run start and map display

## Summary
Trigger a run from the menu, collect party selection, and show a basic floor map.

## Tasks
- Start the gameplay loop when Start/Load Run is selected.
- Open the party picker before showing the floor map.
- Present a simple floor map to choose rooms.

## Acceptance Criteria
- Run button opens a modal PartyPicker and, after confirmation, displays the run ID and map buttons.
- `bun test` covers the new RunMap and PartyPicker components and passes.
