"""
WSGI config for PythonAnywhere deployment.
Copy content to your PythonAnywhere WSGI config file at:
  /home/<your-username>/pythonanywhere_wsgi.py
"""
import os
import sys

project_home = os.path.expanduser('~/kilimo-hub')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kilimo_hub.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
