"""
Configuration WSGI pour le projet softdesk.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'softdesk.settings')

application = get_wsgi_application()
