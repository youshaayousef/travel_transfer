"""
WSGI config for travel_transfer project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_transfer.settings')

application = get_wsgi_application()


"""
import os
import sys
path = '/home/youshaa010yousef/travel_transfer'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'travel_transfer.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
"""