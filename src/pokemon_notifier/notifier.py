from pokemon_notifier.fetcher import Event
import requests, logging
from datetime import datetime
from typing import Protocol


def _format_datetime(value: str | None) -> str:
    if value is None:
        return "Unknown"
    try:
        return datetime.fromisoformat(value).strftime("%m/%d %H:%M")
    except ValueError:
        return value


class Notifier(Protocol):
    def send(self, event: Event, tier: str) -> bool:
        ...

    def send_digest(self, events: list[dict]) -> bool:
        ...

class NtfyNotifier:
    

    def __init__(self, topic: str) -> None:
        self.topic = topic

    def send(self, event: Event, tier: str) -> bool:
        if tier == "instant":
            try:
                response = requests.post(f"https://ntfy.sh/{self.topic}",
                data=f"{event.name}\nStarts: {_format_datetime(event.start)}\nEnds: {_format_datetime(event.end)}",
                headers={
                    "Title": event.heading,
                    "Priority": "3",
                    "Icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Pok%C3%A9_Ball_icon.svg/250px-Pok%C3%A9_Ball_icon.svg.png",
                    "Click": event.link,
                    "Tags": "bell",
                })
                response.raise_for_status()
                return True
            except requests.exceptions.RequestException as http_err:
                logging.error(f"http error occured: {http_err}")
                return False
        else:
            return True

    def send_digest(self, events: list[dict]) -> bool:
        if not events:
            return True
        lines = [
            f"- {e['name']} ({_format_datetime(e['start'])})" for e in events
        ]
        body = "This week's digest:\n" + "\n".join(lines)
        try:
            response = requests.post(f"https://ntfy.sh/{self.topic}",
                data=body,
                headers={
                    "Title": "Weekly Digest",
                    "Priority": "3",
                    "Tags": "calendar",
                    "Click": "https://leekduck.com/events/",
                })
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as http_err:
            logging.error(f"digest send failed: {http_err}")
            return False

def send_notification(event: Event, notifier: Notifier, tier: str) -> bool:
    return notifier.send(event, tier)