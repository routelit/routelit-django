import time

from routelit import RouteLit, RouteLitBuilder

from routelit_django import DjangoSessionStorage, RouteLitDjangoAdapter

# Initialize RouteLit with DjangoSessionStorage
rl = RouteLit(session_storage=DjangoSessionStorage())
# Configure the adapter to use local templates for testing
adapter = RouteLitDjangoAdapter(rl)


def counter_view(ui: RouteLitBuilder):
    ui.title("Django RouteLit Counter")

    # Use session state
    count = ui.session_state.get("count", 0)
    ui.text(f"Current count: {count}")

    if ui.button("Increment"):
        ui.session_state["count"] = count + 1
        ui.rerun()

    if ui.button("Reset"):
        ui.session_state["count"] = 0
        ui.rerun()


def streaming_counter_view(ui: RouteLitBuilder):
    ui.title("Django RouteLit Streaming Counter")

    count = ui.session_state.get("count", 0)
    ui.text(f"Current count: {count}")

    if ui.button("Increment"):
        ui.session_state["count"] = count + 1
        ui.rerun()

    if ui.button("Reset"):
        ui.session_state["count"] = 0
        ui.rerun()

    for i in range(count):
        time.sleep(1)
        ui.text(f"Streaming count: {i + 1}")


def index(request):
    return adapter.response(counter_view, request)


def stream(request):
    return adapter.stream_response(streaming_counter_view, request)
