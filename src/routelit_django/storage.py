import contextvars
from collections.abc import Iterator, MutableMapping
from typing import Any, Optional, cast

# Context variable to hold the current Django session
django_session_ctx: contextvars.ContextVar[Optional[Any]] = contextvars.ContextVar("django_session", default=None)

class DjangoSessionStorage(MutableMapping[str, Any]):
    """
    A RouteLit session storage implementation that delegates to the current Django request session.
    It uses a context variable to access the session of the current request.
    """

    def __init__(self) -> None:
        self._fallback: MutableMapping[str, Any] = {}

    def _get_session(self) -> MutableMapping[str, Any]:
        session = django_session_ctx.get()
        if session is None:
            # Fallback to the local dict if no session is in context (e.g. outside of request)
            return self._fallback
        return cast(MutableMapping[str, Any], session)

    def __getitem__(self, key: str) -> Any:
        return self._get_session()[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._get_session()[key] = value

    def __delitem__(self, key: str) -> None:
        del self._get_session()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._get_session())

    def __len__(self) -> int:
        return len(self._get_session())
