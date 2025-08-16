from _typeshed import Incomplete
from m_crawler.engine.abstract_request import AbstractRequest as AbstractRequest
from playwright.sync_api import Page as Page
from typing import Any, Callable, Sequence

class PlayWeightRequest(AbstractRequest):
    direct_access: Incomplete
    actions: Sequence[Callable[[Page], Any]]
    def __init__(self, url: str, headers: dict[str, str] | None = None, params: dict[str, Any] | None = None, direct_access: bool = True, actions: Sequence[Callable[[Page], Any]] = []) -> None: ...
