from unittest.mock import Mock

import pytest
from django.http import StreamingHttpResponse
from django.test import RequestFactory
from routelit import RouteLit

from routelit_django.adapter import RouteLitDjangoAdapter


@pytest.fixture
def mock_routelit():
    mock_rl = Mock(spec=RouteLit)
    mock_builder = Mock()
    mock_builder.get_client_resource_paths.return_value = []
    mock_rl.get_builder_class.return_value = mock_builder
    mock_rl.client_assets.return_value = []
    mock_rl.default_client_assets.return_value = []
    mock_rl.get_importmap_json.return_value = "{}"
    mock_rl.get_extra_head_content.return_value = ""
    mock_rl.get_extra_body_content.return_value = ""
    return mock_rl


@pytest.fixture
def factory():
    return RequestFactory()


def test_adapter_init(mock_routelit):
    adapter = RouteLitDjangoAdapter(mock_routelit)
    assert adapter.routelit == mock_routelit


def test_response_get(mock_routelit, factory):
    adapter = RouteLitDjangoAdapter(mock_routelit)
    request = factory.get("/")
    request.session = {}

    # Mock RouteLit handle_get_request
    mock_rl_response = Mock()
    mock_rl_response.get_str_json_elements.return_value = "{}"
    mock_rl_response.head.title = "Test"
    mock_rl_response.head.description = "Desc"
    mock_routelit.handle_get_request.return_value = mock_rl_response

    response = adapter.response(Mock(), request)
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.content


def test_response_post(mock_routelit, factory):
    adapter = RouteLitDjangoAdapter(mock_routelit)
    request = factory.post("/", data="{}", content_type="application/json")
    request.session = {}

    mock_routelit.handle_post_request.return_value = [{"type": "action"}]

    response = adapter.response(Mock(), request)
    assert response.status_code == 200
    assert b"action" in response.content


def test_stream_response_post(mock_routelit, factory):
    adapter = RouteLitDjangoAdapter(mock_routelit)
    request = factory.post("/", data="{}", content_type="application/json")
    request.session = {}

    mock_routelit.handle_post_request_stream_jsonl.return_value = iter([b'{"type": "action"}\n'])

    response = adapter.stream_response(Mock(), request)
    assert isinstance(response, StreamingHttpResponse)
    assert response["Content-Type"] == "application/jsonlines"


def test_configure(mock_routelit):
    adapter = RouteLitDjangoAdapter(mock_routelit)
    urlpatterns = []
    adapter.configure(urlpatterns)
    # Should have added at least one pattern for static files
    assert len(urlpatterns) > 0
