from __future__ import annotations
import json
import re
from typing import Any, Callable

from .handlers.web import open_url
from .handlers.apps import open_notepad


def norm(text: str) -> str:
    text = (text or "").lower().strip()
    return re.sub(r"\s+", " ", text)


class CommandDispatcher:
    def __init__(self) -> None:
        self._routes: dict[str, tuple[Callable[..., None], dict[str, Any]]] = {}

        self.register(["открой гугл почту", "открой gmail"], open_url, url="https://mail.google.com/")
        self.register(["открой майл ру", "открой mail ru"], open_url, url="https://mail.ru/")
        self.register(["открой ютуб", "открой youtube"], open_url, url="https://youtube.com/")
        self.register(["открой календарь"], open_url, url="https://calendar.google.com/")
        self.register(["открой блокнот"], open_notepad)
        self.register(["открой лит код", "открой leetcode"], open_url, url="https://leetcode.com/")

        self.grammar_json: str = json.dumps(list(self._routes.keys()), ensure_ascii=False)

    def register(self, phrases: list[str], handler: Callable[..., None], **kwargs: Any) -> None:
        for p in phrases:
            self._routes[norm(p)] = (handler, kwargs)

    def dispatch(self, text: str) -> bool:
        item = self._routes.get(norm(text))
        if not item:
            return False
        fn, kwargs = item
        fn(**kwargs)
        return True
