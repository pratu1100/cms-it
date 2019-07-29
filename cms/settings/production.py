
from .base import *

WSGI_APPLICATION = 'cms.wsgi.production.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'cmsdbinstance.cfxriz5zuq0g.ap-south-1.rds.amazonaws.com',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, 'config', 'db.cnf'),
        },
    }
}