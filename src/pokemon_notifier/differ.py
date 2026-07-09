from pokemon_notifier.fetcher import Event


def find_new_events(events: list[Event], state: dict[str, dict])-> list[Event]:
    store: list[Event] = []
    for item in events:
        if item.event_id in state:
            continue
        else:
            store.append(item)

    return store