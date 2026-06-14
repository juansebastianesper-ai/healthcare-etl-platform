import os, sys
from django.core.wsgi import get_wsgi_application

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ.setdefault('SECRET_KEY', 'django-insecure-default-key')
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('DJANGO_ALLOWED_HOSTS', '.pythonanywhere.com,localhost')

application = get_wsgi_application()
