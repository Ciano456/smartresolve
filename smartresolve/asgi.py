# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

"""
ASGI config for smartresolve project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartresolve.settings")

application = get_asgi_application()
