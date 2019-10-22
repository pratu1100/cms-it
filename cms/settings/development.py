
from .base import *

WSGI_APPLICATION = 'cms.wsgi.development.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'kjsce-cms.database.windows.net',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, 'config', 'db.cnf'),
        },
    }
}
