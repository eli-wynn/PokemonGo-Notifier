import os
from datetime import datetime, timezone
from pathlib import Path

from pokemon_notifier.fetcher import fetch_raw_events, parse_events
from pokemon_notifier.differ import find_new_events
from pokemon_notifier.state import load_state, save_state
from pokemon_notifier.filter import load_tier_config, classify_event
from pokemon_notifier.notifier import NtfyNotifier, send_notification

STATE_PATH = Path("state.json")
TIERS_PATH = Path("tiers.toml")
SUNDAY = 6


def main() -> None:
    #loading phase
    state = load_state(STATE_PATH)
    tier_map, default_tier = load_tier_config(TIERS_PATH)
    notifier = NtfyNotifier(os.environ["NTFY_TOPIC"])

    #fetch Phase
    events = parse_events(fetch_raw_events())

    #diff phase
    new_events = find_new_events(events, state)

    #classification and notification
    for event in new_events:
        tier = classify_event(event, tier_map, default_tier)
        if send_notification(event, notifier, tier):
            state[event.event_id] = {
                "notified_at": datetime.now(timezone.utc).isoformat(),
                "tier": tier,
                "digest_sent": tier != "digest",
                "name": event.name,
                "link": event.link,
                "start": event.start,
                "end": event.end,
            }

    #weekly digest phase
    today = datetime.now(timezone.utc).date()
    if today.weekday() == SUNDAY and state.get("last_digest_sent") != today.isoformat():
        pending = [
            record for key, record in state.items()
            if key != "last_digest_sent"
            and record.get("tier") == "digest"
            and not record.get("digest_sent", True)
        ]
        if notifier.send_digest(pending):
            for record in pending:
                record["digest_sent"] = True
            state["last_digest_sent"] = today.isoformat()

    save_state(STATE_PATH, state)


if __name__ == "__main__":
    main()
