import json

import pytest
from django.test import RequestFactory
from routelit import COOKIE_SESSION_KEY

from routelit_django.request import DjangoRouteLitRequest


@pytest.fixture
def factory():
    return RequestFactory()


def test_get_headers(factory):
    request = factory.get("/", HTTP_X_CUSTOM="value")
    rl_request = DjangoRouteLitRequest(request)
    headers = rl_request.get_headers()
    # Django normalizes headers to title case (X-Custom), not uppercase
    assert headers["X-Custom"] == "value"


def test_method(factory):
    request = factory.post("/")
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.method == "POST"


def test_get_json(factory):
    data = {"foo": "bar"}
    request = factory.post("/", data=json.dumps(data), content_type="application/json")
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.get_json() == data


def test_get_json_invalid(factory):
    request = factory.post("/", data="invalid json", content_type="application/json")
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.get_json() is None


def test_get_json_multipart(factory):
    data = {"foo": "bar"}
    # Letting factory handle boundary
    request = factory.post("/", data={"json": json.dumps(data)})
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.get_json() == data


def test_get_json_multipart_invalid(factory):
    request = factory.post("/", data={"json": "invalid json"})
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.get_json() == {}


def test_is_json(factory):
    request = factory.post("/", content_type="application/json")
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.is_json() is True


def test_is_multipart(factory):
    request = factory.post(
        "/", data={"foo": "bar"}
    )  # Default is multipart if data is dict? Actually factory default is multipart/form-data
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.is_multipart() is True


def test_get_query_param(factory):
    request = factory.get("/?param=value")
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.get_query_param("param") == "value"


def test_get_query_param_list(factory):
    request = factory.get("/?param=v1&param=v2")
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.get_query_param_list("param") == ["v1", "v2"]


def test_get_pathname(factory):
    request = factory.get("/test/path/")
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.get_pathname() == "/test/path/"


def test_get_files(factory):
    from django.core.files.uploadedfile import SimpleUploadedFile

    f1 = SimpleUploadedFile("file1.txt", b"content1")
    f2 = SimpleUploadedFile("file2.txt", b"content2")
    # Removing explicit content_type to let factory set boundary
    request = factory.post("/", data={"files": [f1, f2]})
    rl_request = DjangoRouteLitRequest(request)
    files = rl_request.get_files()
    assert len(files) == 2
    assert files[0].name == "file1.txt"


def test_get_referrer(factory):
    request = factory.get("/", HTTP_REFERER="http://example.com")
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.get_referrer() == "http://example.com"


def test_get_host(factory):
    request = factory.get("/", HTTP_HOST="testserver")
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.get_host() == "testserver"


def test_get_session_id(factory):
    request = factory.get("/")
    request.COOKIES[COOKIE_SESSION_KEY] = "test-session"
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.get_session_id() == "test-session"


def test_get_session_id_default(factory):
    request = factory.get("/")
    rl_request = DjangoRouteLitRequest(request)
    session_id = rl_request.get_session_id()
    assert session_id is not None
    import uuid

    uuid.UUID(session_id)


def test_get_path_params(factory):
    request = factory.get("/")

    class MockMatch:
        def __init__(self):
            self.kwargs = {"id": "123"}

    request.resolver_match = MockMatch()
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.get_path_params() == {"id": "123"}


def test_get_path_params_none(factory):
    request = factory.get("/")
    rl_request = DjangoRouteLitRequest(request)
    assert rl_request.get_path_params() is None
