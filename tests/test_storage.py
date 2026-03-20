from routelit_django.storage import DjangoSessionStorage, django_session_ctx


def test_storage_outside_context():
    storage = DjangoSessionStorage()
    # Should fallback to an empty dict if no session is set
    storage["key"] = "value"
    assert storage["key"] == "value"
    assert "key" in storage
    del storage["key"]
    assert "key" not in storage


def test_storage_inside_context():
    session = {"foo": "bar"}
    storage = DjangoSessionStorage()

    token = django_session_ctx.set(session)
    try:
        assert storage["foo"] == "bar"
        storage["new"] = "val"
        assert session["new"] == "val"
    finally:
        django_session_ctx.reset(token)

    # Outside context it should be empty again
    assert "foo" not in storage
