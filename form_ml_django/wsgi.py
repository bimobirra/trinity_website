import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'form_ml_django.settings')

application = get_wsgi_application()
