"""
Configuration ASGI pour le projet softdesk.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'softdesk.settings')

application = get_asgi_application()
