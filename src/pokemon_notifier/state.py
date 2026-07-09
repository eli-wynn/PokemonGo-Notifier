import json
from pathlib import Path


def load_state(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_state(path: Path, state: dict[str, dict]) -> None:
    path.write_text(json.dumps(state, indent=2, sort_keys=True))