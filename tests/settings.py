SECRET_KEY = "test-secret-key"  # noqa: S105
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "routelit_django",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]
