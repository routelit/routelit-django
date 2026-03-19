# API Reference

This page contains the API reference documentation for the RouteLit Django adapter.

## RouteLitDjangoAdapter

::: routelit_django.adapter.RouteLitDjangoAdapter
    handler: python
    options:
        members:
            - __init__
            - configure
            - configure_static_assets
            - response
            - stream_response
        show_root_heading: true
        show_source: false
        heading_level: 3

## DjangoSessionStorage

::: routelit_django.storage.DjangoSessionStorage
    handler: python
    options:
        show_root_heading: true
        show_source: false
        heading_level: 3

## DjangoRouteLitRequest

::: routelit_django.request.DjangoRouteLitRequest
    handler: python
    options:
        members:
            - __init__
            - get_headers
            - get_path_params
            - get_referrer
            - get_json
            - get_files
            - is_json
            - is_multipart
            - get_query_param
            - get_query_param_list
            - get_session_id
            - get_pathname
            - get_host
            - method
        show_root_heading: true
        show_source: false
        heading_level: 3

## RunMode

::: routelit_django.adapter.RunMode
    handler: python
    options:
        show_root_heading: true
        show_source: false
        heading_level: 3

## RunModeEnum

::: routelit_django.adapter.RunModeEnum
    handler: python
    options:
        show_root_heading: true
        show_source: false
        heading_level: 3

## Exports

The following are exported from the `routelit_django` package:

```python
from routelit_django import (
    RouteLitDjangoAdapter,    # Main adapter class
    DjangoSessionStorage,     # Session storage implementation
    DjangoRouteLitRequest,    # Request wrapper
    RunMode,                  # Literal type for run modes
    RunModeEnum,              # Enum for run modes
)
```
