"""WSGI entry point for the local Milestone A web surface."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "datara.settings")

application = get_wsgi_application()
