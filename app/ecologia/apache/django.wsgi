import os
import sys

path = '/home/victor/app_oe/ecologia/'
sys.path.insert(0,path)
if path not in sys.path:
    sys.path.insert(0,path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

