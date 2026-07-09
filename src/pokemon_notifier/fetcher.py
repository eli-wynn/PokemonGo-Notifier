import requests, json, logging
from dataclasses import dataclass
from datetime import datetime

SCRAPEDDUCK_EVENTS_URL = "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/data/events.json"


@dataclass(frozen=True)
class Event:
    event_id: str
    name: str
    event_type: str
    heading: str | None
    link: str | None
    start: str | datetime | None
    end: str | datetime | None

def fetch_raw_events(url: str = SCRAPEDDUCK_EVENTS_URL) -> list[dict]:
    x = requests.get(url)
    x.raise_for_status()
    lister = json.loads(x.text)
    return lister

def parse_events(raw: list[dict]) -> list[Event]:
    store: list[Event] = []
    for item in raw:
        event_id = item.get("eventID")
        if event_id is None:
            logging.warning("Key Error detected with "+item.get("name", "<unknown>"))
            continue
        temp = Event(event_id=event_id,
                name=item.get("name", "Unknown Name"),
                event_type=item.get("eventType", "Unknown Event Type"),
                heading=item.get("heading"),
                link=item.get("link"),
                start=item.get("start", "Date not found"),
                end=item.get("end", "No End Date"))
        store.append(temp)
    return store