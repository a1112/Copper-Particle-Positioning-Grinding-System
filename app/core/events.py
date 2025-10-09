from dataclasses import dataclass
from typing import Any, Callable, Dict, List, DefaultDict
from collections import defaultdict

class EventBus:
    def __init__(self) -> None:
        self._subs: DefaultDict[str, List[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable[[Any], None]) -> None:
        self._subs[topic].append(handler)

    def publish(self, topic: str, payload: Any) -> None:
        for h in list(self._subs.get(topic, [])):
            h(payload)

# Common topics
TOPIC_TARGET_FOUND = 'vision.target_found'  # payload: dict(x, y, theta, score)
TOPIC_PROCESS_EVENT = 'process.event'       # payload: dict(event, data)
