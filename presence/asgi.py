"""
ASGI config for presence project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

import pymysql  # import pymysql

pymysql.install_as_MySQLdb()  # call this method before any Django import


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presence.settings')

application = get_asgi_application()
app = application
