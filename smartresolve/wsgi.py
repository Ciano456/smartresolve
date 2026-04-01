# Student Name: Cian O'Connor
# Student Number: x22109668
# Module: Final Year Project

"""
WSGI config for smartresolve project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartresolve.settings")

application = get_wsgi_application()
