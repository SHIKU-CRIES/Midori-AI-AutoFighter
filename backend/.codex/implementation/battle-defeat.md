# Battle defeat handling

`BattleRoom.resolve` reports a `"defeat"` result when all party members have zero or less HP. `_run_battle` checks for this outcome, clears pending state flags, saves the final snapshot with `ended: true`, and removes the run from storage.
