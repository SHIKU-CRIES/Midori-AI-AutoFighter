# Battle polling

The `pollBattle` routine in `routes/+page.svelte` continuously polls the backend
for combat snapshots. It now tracks consecutive polls where combat has ended but
no rewards or completion flags have arrived. After roughly three seconds of
such stalled polling, the function stops the battle, records an error on the
snapshot, and logs a warning so the reward overlay or reset flow can proceed.

