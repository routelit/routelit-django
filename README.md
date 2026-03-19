# RouteLit Django Adapter

A Django adapter for the RouteLit framework, enabling seamless integration of RouteLit's reactive UI components with Django web applications.

## ✨ Features

- **Standard HTTP Support**: Full page loads and JSON interactions.
- **HTTP Streaming**: Progressive UI updates using `StreamingHttpResponse`.
- **Django Session Integration**: Persistent state management using Django's session backend.
- **Static Asset Serving**: Automated configuration for serving RouteLit client assets.

## 🚀 Installation

```bash
pip install routelit routelit-django
```

## 📖 Usage

### 1. Configure RouteLit

In your `views.py`:

```python
from routelit import RouteLit, RouteLitBuilder
from routelit_django import RouteLitDjangoAdapter, DjangoSessionStorage

# Initialize RouteLit with DjangoSessionStorage
rl = RouteLit(session_storage=DjangoSessionStorage())
adapter = RouteLitDjangoAdapter(rl)

def my_view(ui: RouteLitBuilder):
    ui.title("Hello RouteLit!")
    if ui.button("Click me"):
        ui.text("Clicked!")

def index(request):
    return adapter.response(my_view, request)

def stream(request):
    return adapter.stream_response(my_view, request)
```

### 2. Configure URLs

In your `urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('stream/', views.stream, name='stream'),
]

# Register static assets
views.adapter.configure(urlpatterns)
```

### 3. Add to Installed Apps

In your `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'routelit_django',
]
```

## 🏗️ Architecture

The Django adapter translates Django's `HttpRequest` into `RouteLitRequest` and handles the response generation using Django's `HttpResponse`, `JsonResponse`, and `StreamingHttpResponse`.

By using `DjangoSessionStorage`, the application state is stored directly in the user's Django session, making it compatible with any session backend (database, cache, etc.).
