# Backend run logging and metrics

We need more comprehensive telemetry for player runs.

## Tasks
- Coder, record which character is chosen at the start of each run and write it to the run history table.
- Coder, log every battle in the run, labeling weak encounters and bosses separately.
- Coder, persist cumulative counts for total battles, weak battles, and bosses defeated to the database at run end.
- Coder, add retrieval methods or endpoints to surface these metrics for analytics.
- Reviewer, add or extend tests to cover the new logging paths.
