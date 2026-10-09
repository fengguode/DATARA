"""WSGI entry point for the local DATARA application.

The process-local limiter is supported through the constrained runserver
entry point only. This marker rejects an ordinary direct WSGI launch; an
operator who deliberately sets it can bypass the convention, so it is not a
security boundary or evidence of a safe runtime topology.
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "datara.settings")

def _application():
    if os.environ.get("DATARA_LOCAL_SINGLE_PROCESS_SERVER") != "1":
        raise RuntimeError(
            "Direct WSGI hosting is unsupported for the process-local read limiter; "
            "start the loopback-only single-process local server through manage.py."
        )

    from django.core.wsgi import get_wsgi_application

    return get_wsgi_application()


application = _application()
