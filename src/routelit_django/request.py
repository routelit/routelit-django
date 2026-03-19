import json
import uuid
from collections.abc import Mapping
from io import IOBase
from typing import Any, Optional, cast

from django.http import HttpRequest
from routelit import COOKIE_SESSION_KEY, RouteLitRequest


class DjangoRouteLitRequest(RouteLitRequest):
    """
    Implements the RouteLitRequest interface for Django.
    """

    def __init__(self, request: HttpRequest):
        self.request = request
        super().__init__()
        self.__default_session_id = str(uuid.uuid4())

    def get_headers(self) -> dict[str, str]:
        # Django 2.2+ has request.headers
        if hasattr(self.request, "headers"):
            return dict(self.request.headers)
        # Fallback for older Django if needed, though we targeted 4.0+
        return {
            key[5:].replace("_", "-"): cast(str, value)
            for key, value in self.request.META.items()
            if key.startswith("HTTP_")
        }

    def get_path_params(self) -> Optional[Mapping[str, Any]]:
        if hasattr(self.request, "resolver_match") and self.request.resolver_match:
            return cast(Mapping[str, Any], self.request.resolver_match.kwargs)
        return None

    def get_referrer(self) -> Optional[str]:
        return cast(Optional[str], self.request.META.get("HTTP_REFERER"))

    @property
    def method(self) -> str:
        return cast(str, self.request.method)

    def get_json(self) -> Optional[Any]:
        if self.is_json():
            try:
                return json.loads(self.request.body)
            except (json.JSONDecodeError, AttributeError):
                return None
        if self.is_multipart():
            json_str = self.request.POST.get("json", "{}")
            try:
                return json.loads(cast(str, json_str))
            except json.JSONDecodeError:
                return {}
        return None

    def get_files(self) -> Optional[list[IOBase]]:
        if self.is_multipart():
            return cast(list[IOBase], self.request.FILES.getlist("files"))
        return None

    def is_json(self) -> bool:
        content_type = self.request.content_type or ""
        return content_type.startswith("application/json")

    def is_multipart(self) -> bool:
        content_type = self.request.content_type or ""
        return content_type.startswith("multipart/form-data")

    def get_query_param(self, key: str) -> Optional[str]:
        return cast(Optional[str], self.request.GET.get(key))

    def get_query_param_list(self, key: str) -> list[str]:
        return cast(list[str], self.request.GET.getlist(key))

    def get_session_id(self) -> str:
        return cast(str, self.request.COOKIES.get(COOKIE_SESSION_KEY, self.__default_session_id))

    def get_pathname(self) -> str:
        return cast(str, self.request.path)

    def get_host(self) -> str:
        return cast(str, self.request.get_host())
