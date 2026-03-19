# RouteLit Django Adapter

[![Release](https://img.shields.io/github/v/release/routelit/routelit-django)](https://img.shields.io/github/v/release/routelit/routelit-django)
[![Build status](https://img.shields.io/github/actions/workflow/status/routelit/routelit-django/main.yml?branch=main)](https://github.com/routelit/routelit-django/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/routelit/routelit-django/branch/main/graph/badge.svg)](https://codecov.io/gh/routelit/routelit-django)
[![Commit activity](https://img.shields.io/github/commit-activity/m/routelit/routelit-django)](https://img.shields.io/github/commit-activity/m/routelit/routelit-django)
[![License](https://img.shields.io/github/license/routelit/routelit-django)](https://img.shields.io/github/license/routelit/routelit-django)

A Django adapter for the RouteLit framework, enabling seamless integration of RouteLit's reactive UI components with Django web applications.

## Installation

```bash
pip install routelit routelit-django
```

## Quick Start

Here's a complete example to get you started:

```python
from django.urls import path
from django.http import HttpRequest
from routelit import RouteLit, RouteLitBuilder
from routelit_django import RouteLitDjangoAdapter, DjangoSessionStorage

# Initialize RouteLit with DjangoSessionStorage
rl = RouteLit(session_storage=DjangoSessionStorage())

# Create and configure the adapter
adapter = RouteLitDjangoAdapter(rl)

# Define your view function
def build_hello_view(ui: RouteLitBuilder):
    name = ui.text_input(label="What is your name", placeholder="John", default_value="")
    ui.write(f"Hello {name}")
    if ui.button("Submit"):
        ui.write("Thanks for your submission!")

def index(request: HttpRequest):
    return adapter.response(build_hello_view, request)

# Configure the adapter with your URL patterns
urlpatterns = [
    path('', index, name='index'),
]

# Register static assets
adapter.configure(urlpatterns)
```

## Features

- **Framework Agnostic**: Works seamlessly with Django
- **Declarative UI**: Build interfaces using simple Python functions with a builder pattern
- **Interactive Components**: Buttons, forms, inputs, selects, checkboxes, containers, columns, etc.
- **State Management**: Built-in session state management with Django session integration
- **Reactive Updates**: Automatic UI updates based on user interactions
- **HTTP Streaming**: Support for streaming responses using `StreamingHttpResponse`
- **Development Mode**: Hot reloading support for frontend development

## Usage

### Basic View Registration

```python
from django.urls import path
from routelit import RouteLit, RouteLitBuilder
from routelit_django import RouteLitDjangoAdapter, DjangoSessionStorage

# Initialize RouteLit with DjangoSessionStorage
rl = RouteLit(session_storage=DjangoSessionStorage())
adapter = RouteLitDjangoAdapter(rl)

def counter_view(ui: RouteLitBuilder):
    if "counter" not in ui.session_state:
        ui.session_state["counter"] = 0

    counter = ui.session_state["counter"]
    ui.markdown(f"## Count: {counter}")

    if ui.button("Increment", key="inc"):
        ui.session_state["counter"] = counter + 1
        ui.rerun()

def counter(request: HttpRequest):
    return adapter.response(counter_view, request)

urlpatterns = [
    path('counter/', counter, name='counter'),
]

# Register static assets
adapter.configure(urlpatterns)
```

### Streaming Views

For HTTP streaming responses:

```python
def stream_view(ui: RouteLitBuilder):
    for i in range(10):
        ui.text(f"Count: {i}")

def stream(request: HttpRequest):
    return adapter.stream_response(stream_view, request)

urlpatterns = [
    path('stream/', stream, name='stream'),
]

adapter.configure(urlpatterns)
```

### Development Mode

For development with hot reloading of the frontend:

```python
adapter = RouteLitDjangoAdapter(
    routelit,
    run_mode="dev_client",
    local_frontend_server="http://localhost:5173"
)
```

## Configuration Options

When creating the adapter, you can configure the following options:

| Parameter                 | Type                   | Default             | Description                                         |
| ------------------------- | ---------------------- | ------------------- | --------------------------------------------------- |
| `static_path`             | `str \| None`          | Auto-detected       | Custom path for static assets                       |
| `template_path`           | `str`                  | Auto-detected       | Custom path for templates                           |
| `run_mode`                | `str`                  | `"prod"`            | One of `"prod"`, `"dev_client"`, `"dev_components"` |
| `local_frontend_server`   | `str \| None`          | `None`              | URL of local Vite dev server (for dev mode)         |
| `local_components_server` | `str \| None`          | `None`              | URL of local components dev server (for dev mode)   |
| `cookie_config`           | `CookieConfig \| None` | Production defaults | Custom cookie configuration                         |

### Run Modes

- **`prod`**: Production mode with secure cookie settings
- **`dev_client`**: Development mode for the client with hot reloading
- **`dev_components`**: Development mode for the components

### Cookie Configuration

In production mode, the default cookie configuration is:

```python
{
    "secure": True,
    "samesite": "none",
    "httponly": True,
    "max_age": 60 * 60 * 24 * 1,  # 1 day
}
```

You can override these settings:

```python
adapter = RouteLitDjangoAdapter(
    routelit,
    cookie_config={
        "secure": False,
        "max_age": 3600,  # 1 hour
    }
)
```

## Example Application

Check out the [example application](https://github.com/routelit/routelit-django/tree/main/examples) in the repository for a complete working example with:

- Counter example using standard responses
- Streaming counter example with real-time updates
- Multiple route patterns

## License

Apache-2.0 License

## Maintainer

Maintained by [@rolangom](https://x.com/rolangom).
