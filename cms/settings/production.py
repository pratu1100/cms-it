
from .base import *

WSGI_APPLICATION = 'cms.wsgi.production.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'ls-7aad48b2eded0671a0c5ce6fcde3e04bbabc6957.cu7csf8tsbsu.ap-south-1.rds.amazonaws.com',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, 'config', 'db.cnf'),
        },
    }
}