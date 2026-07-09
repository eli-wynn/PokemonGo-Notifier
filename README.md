# PokemonGo-Notifier

A zero-cost pipeline that sends a push notification to your phone whenever a
new Pokémon GO event is announced. Runs on a GitHub Actions cron schedule —
no servers, no hosting costs.

- **Data source**: [ScrapedDuck](https://github.com/bigfoott/ScrapedDuck), an
  open-source scraper that publishes LeekDuck event data as JSON on its
  `data` branch.
- **Notifications**: [ntfy.sh](https://ntfy.sh) — push notifications via a
  simple HTTP POST to a topic.
- **State**: new/already-seen events are tracked in `state.json`, committed
  back to the repo by the workflow after each run.

## How it works

1. **Fetch** — pulls the latest events JSON from ScrapedDuck and parses it
   into `Event` objects (`fetcher.py`).
2. **Diff** — compares fetched events against `state.json` to find events
   that haven't been seen before (`differ.py`).
3. **Classify** — looks up each new event's type in `tiers.toml` to decide
   its tier: `instant`, `digest`, or a configured default (`filter.py`).
4. **Notify** — `instant`-tier events get an immediate high-priority push.
   `digest`-tier events are held in `state.json` and released as a single
   combined notification every Sunday (`notifier.py`).
5. **Save** — updates `state.json` so nothing is ever notified twice.

All of the above is orchestrated by `main.py`, run on a schedule by
`.github/workflows/notify.yml`.

## Project layout

```
src/pokemon_notifier/
  fetcher.py    # ScrapedDuck fetch + Event model
  differ.py     # new-event detection against state
  state.py      # state.json load/save
  filter.py     # tiers.toml loading + tier classification
  notifier.py   # Notifier protocol + ntfy implementation
  main.py       # orchestration entry point
tiers.toml      # tier config: which event types are instant/digest
.github/workflows/notify.yml   # cron schedule + commit-back workflow
```

## Setup

**Requirements**: Python 3.11+

1. Install the project (in a virtualenv):
   ```
   pip install -e ".[dev]"
   ```
2. Pick a hard-to-guess ntfy topic name and subscribe to it in the
   [ntfy app](https://ntfy.sh) — topics are unauthenticated by default, so
   anyone who knows the exact name can read or publish to it.
3. Set `NTFY_TOPIC` locally to test:
   ```powershell
   $env:NTFY_TOPIC = "your-topic-name-here"
   ```
4. Run it:
   ```
   python -m pokemon_notifier.main
   ```

## Configuring tiers

Edit `tiers.toml` to control which ScrapedDuck `eventType` values trigger an
instant push, which go into the weekly digest, and what happens to event
types that aren't listed at all (`default_tier`).

## GitHub Actions setup

The workflow needs one repo secret and one permissions check, both done in
GitHub's UI (not in this repo):

1. **Add the secret**: Settings → Secrets and variables → Actions → New
   repository secret → name `NTFY_TOPIC`, value = your real topic.
2. **Confirm write permissions**: Settings → Actions → General → Workflow
   permissions must allow read/write, or the workflow's commit-back step
   (which pushes updated `state.json`) will fail.

The workflow runs every 4 hours (`0 */4 * * *`, UTC) and can also be
triggered manually from the Actions tab (`workflow_dispatch`).

## Known limitations (v1)

- No automated test suite yet.
- A ScrapedDuck outage or malformed response will fail that run's job
  outright rather than degrading gracefully — it'll just pick back up on the
  next scheduled run.
- State is a single JSON file committed to the repo; noted as swappable for
  a real database later if needed.
