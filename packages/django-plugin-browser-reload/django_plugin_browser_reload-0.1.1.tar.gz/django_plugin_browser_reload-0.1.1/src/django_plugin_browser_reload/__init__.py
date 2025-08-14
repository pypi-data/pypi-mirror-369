from django.urls import include, path

import djp


@djp.hookimpl
def installed_apps():
    return ["django_browser_reload"]


@djp.hookimpl
def urlpatterns():
    return [
        path("__reload__/", include("django_browser_reload.urls")),
    ]


@djp.hookimpl
def settings(current_settings: dict):
    # "Ensure you have "django.contrib.staticfiles" in your INSTALLED_APPS.""
    installed_apps: list = current_settings.setdefault("INSTALLED_APPS", [])
    if "django.contrib.staticfiles" not in installed_apps:
        installed_apps.append("django.contrib.staticfiles")

    current_settings.setdefault("STATIC_URL", "static/")

    # "The middleware should be listed after any others that encode the response, such as Django’s GZipMiddleware."
    current_settings["MIDDLEWARE"] = _inject_middleware(current_settings["MIDDLEWARE"])


def _inject_middleware(current_middleware: list[str]) -> list[str]:
    """Inject BrowserReloadMiddleware early, but not too early."""
    MUST_GO_AFTER = [
        "django.middleware.gzip.GZipMiddleware",
    ]
    position = max(_next_index_or_start(current_middleware, mw) for mw in MUST_GO_AFTER)

    return [
        *current_middleware[:position],
        "django_browser_reload.middleware.BrowserReloadMiddleware",
        *current_middleware[position:],
    ]


def _next_index_or_start(lst: list, item):
    try:
        return lst.index(item) + 1
    except ValueError:
        return 0
