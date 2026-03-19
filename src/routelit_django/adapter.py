import importlib.resources as resources
import os
from collections.abc import AsyncGenerator, Generator
from enum import Enum
from typing import Any, Literal, Optional, Union

from django.http import HttpRequest, HttpResponse, HttpResponseBase, JsonResponse, StreamingHttpResponse
from django.urls import re_path
from django.views.static import serve
from routelit import COOKIE_SESSION_KEY, RouteLit, ViewFn

from .request import DjangoRouteLitRequest
from .storage import django_session_ctx
from .utils import (
    get_default_static_path,
    get_default_template_path,
)

production_cookie_config: dict[str, Any] = {
    "secure": True,
    "samesite": "None",
    "httponly": True,
    "max_age": 60 * 60 * 24 * 1,  # 1 day
}

RunMode = Literal["prod", "dev_client", "dev_components"]


class RunModeEnum(Enum):
    PROD = "prod"
    DEV_CLIENT = "dev_client"
    DEV_COMPONENTS = "dev_components"


class RouteLitDjangoAdapter:
    """
    A Django adapter for the RouteLit framework, enabling seamless integration of RouteLit's reactive UI components with Django web applications.
    """

    def __init__(
        self,
        routelit: RouteLit,
        *,
        static_path: Optional[str] = None,
        template_path: str = get_default_template_path(),
        run_mode: RunMode = "prod",
        local_frontend_server: Optional[str] = None,
        local_components_server: Optional[str] = None,
        cookie_config: Optional[dict[str, Any]] = None,
    ):
        self.routelit = routelit
        self.static_path = static_path or get_default_static_path()
        self.template_path = template_path
        self.run_mode = run_mode
        self.local_frontend_server = local_frontend_server
        self.local_components_server = local_components_server
        self.cookie_config = {**production_cookie_config, **(cookie_config or {})} if run_mode == "prod" else {}

    def configure(self, urlpatterns: list[Any]) -> "RouteLitDjangoAdapter":
        """
        Configure the Django application to use the RouteLitDjangoAdapter.
        This adds the necessary URL patterns for static assets.
        """
        for asset_target in self.routelit.get_builder_class().get_client_resource_paths():
            package_name, path_str = asset_target["package_name"], asset_target["path"]
            assets_path = resources.files(package_name).joinpath(path_str)
            urlpatterns.append(
                re_path(
                    f"^routelit/{package_name}/(?P<path>.*)$",
                    serve,
                    {"document_root": str(assets_path)},
                    name=f"routelit_assets_{package_name}",
                )
            )

        urlpatterns.append(
            re_path(
                r"^routelit/(?P<path>.*)$",
                serve,
                {"document_root": self.static_path},
                name="routelit_static",
            )
        )
        return self

    def _handle_get_request(self, view_fn: ViewFn, request: DjangoRouteLitRequest, **kwargs: Any) -> HttpResponse:
        rl_response = self.routelit.handle_get_request(view_fn, request, **kwargs)

        # We need to ensure the template path is available to Django
        # For now, we'll try to use render, but we might need a custom loader or engine
        context = {
            "ROUTELIT_DATA": rl_response.get_str_json_elements(),
            "PAGE_TITLE": rl_response.head.title,
            "PAGE_DESCRIPTION": rl_response.head.description,
            "RUN_MODE": self.run_mode,
            "LOCAL_FRONTEND_SERVER": self.local_frontend_server or "",
            "LOCAL_COMPONENTS_SERVER": self.local_components_server or "",
            "default_vite_assets": self.routelit.default_client_assets(),
            "importmap_json": self.routelit.get_importmap_json(),
            "vite_assets": self.routelit.client_assets(),
            "extra_head_content": self.routelit.get_extra_head_content(),
            "extra_body_content": self.routelit.get_extra_body_content(),
            # CSRF token is expected to be available via Django's context processor
            # when {% csrf_token %} is used in the template.
        }

        # Django's render requires the template to be in TEMPLATE dirs or apps
        # Since we are a library, we might need to use a custom engine or render_to_string with full path
        from django.template import engines

        template_file = os.path.join(self.template_path, "index.html")
        with open(template_file) as f:
            template_content = f.read()

        # Using the first configured engine
        engine = engines.all()[0]
        template = engine.from_string(template_content)
        content = template.render(context, request.request)

        response = HttpResponse(content)

        # Set session cookie
        cookie_kwargs: dict[str, Any] = {
            "key": COOKIE_SESSION_KEY,
            "value": request.get_session_id(),
        }
        if self.run_mode == "prod":
            cookie_kwargs.update({
                "secure": self.cookie_config.get("secure", True),
                "httponly": self.cookie_config.get("httponly", True),
                "samesite": self.cookie_config.get("samesite", "None"),
                "max_age": self.cookie_config.get("max_age"),
            })

        response.set_cookie(**cookie_kwargs)
        return response

    def response(
        self,
        view_fn: ViewFn,
        request: HttpRequest,
        inject_builder: Optional[bool] = None,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        token = django_session_ctx.set(request.session)
        try:
            req = DjangoRouteLitRequest(request)
            if req.method == "POST":
                actions = self.routelit.handle_post_request(view_fn, req, inject_builder, *args, **kwargs)
                return JsonResponse(actions, safe=False)
            return self._handle_get_request(view_fn, req, **kwargs)
        finally:
            django_session_ctx.reset(token)

    def stream_response(
        self,
        view_fn: ViewFn,
        request: HttpRequest,
        inject_builder: Optional[bool] = None,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseBase:
        req = DjangoRouteLitRequest(request)
        if req.method == "POST":
            session = request.session

            def stream_with_session() -> Union[Generator[Any, None, None], AsyncGenerator[Any, None]]:
                token = django_session_ctx.set(session)
                try:
                    yield from self.routelit.handle_post_request_stream_jsonl(
                        view_fn, req, inject_builder, *args, **kwargs
                    )
                finally:
                    django_session_ctx.reset(token)

            return StreamingHttpResponse(
                stream_with_session(),
                content_type="application/jsonlines",
            )

        token = django_session_ctx.set(request.session)
        try:
            res: HttpResponseBase = self._handle_get_request(view_fn, req, **kwargs)
            return res
        finally:
            django_session_ctx.reset(token)
