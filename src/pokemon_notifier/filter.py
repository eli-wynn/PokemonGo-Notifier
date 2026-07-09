import tomllib
from pathlib import Path
from pokemon_notifier.fetcher import Event

def load_tier_config(path: Path) -> tuple[dict[str, str], str]:
    with path.open("rb") as f: data = tomllib.load(f)
    book : dict[str, str] = {}
    tierList = data["tiers"]
    for tier_name, tier_body in tierList.items():
        tierBody = tier_body["event_types"]
        for x in tierBody:
            book[x] = tier_name
        
    return book, data["default_tier"]



def classify_event(event: Event, tier_map: dict[str, str], default_tier: str) -> str:
    id = event.event_type
    if id in tier_map:
        return tier_map[id]
    else:
        return default_tier