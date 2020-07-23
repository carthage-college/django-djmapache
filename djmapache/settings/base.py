# -*- coding: utf-8 -*-

"""Django settings for project."""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

# sqlserver connection string
from djimix.settings.local import LENEL_EARL, MSSQL_EARL
from djimix.settings.local import INFORMIX_ODBC, INFORMIX_ODBC_TRAIN
from djimix.settings.local import INFORMIX_ODBC_JXPROD, INFORMIX_ODBC_JXTEST
from djimix.settings.local import (
    INFORMIXSERVER,
    DBSERVERNAME,
    INFORMIXDIR,
    ODBCINI,
    ONCONFIG,
    INFORMIXSQLHOSTS,
    LD_LIBRARY_PATH,
    LD_RUN_PATH,
)

# Debug
DEBUG = False
INFORMIX_DEBUG = 'debug'
ADMINS = (
    ('', ''),
)
MANAGERS = ADMINS

SECRET_KEY = ''
ALLOWED_HOSTS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
SITE_ID = 1
USE_I18N = False
USE_L10N = False
USE_TZ = False
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'
SERVER_URL = ''
API_URL = '{0}/{0}'.format(SERVER_URL, 'api')
LIVEWHALE_API_URL = 'https://{}'.format(SERVER_URL)
STATIC_URL = 'https://{0}/static/djmapache/'.format(SERVER_URL)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(__file__)
ADMIN_MEDIA_PREFIX = '/static/admin/'
ROOT_URL = '/apps/mapache/'
MEDIA_ROOT = '{0}/assets/'.format(BASE_DIR)
MEDIA_URL = '/media/djmapache/'.format(ROOT_URL)
STATIC_ROOT = '{0}/static/'.format(ROOT_DIR)
UPLOADS_DIR = '{0}files/'.format(MEDIA_ROOT)
UPLOADS_URL = '{0}files/'.format(MEDIA_URL)
ROOT_URLCONF = 'djmapache.core.urls'
WSGI_APPLICATION = 'djmapache.wsgi.application'
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
DATABASES = {
    'default': {
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'NAME': 'django_djmapache',
        'ENGINE': 'django.db.backends.mysql',
        #'ENGINE': 'django.db.backends.dummy',
        'USER': '',
        'PASSWORD': ''
    },
}
INSTALLED_APPS = [
    'bootstrap4',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'djmapache.core',
    # needed for template tags
    'djtools',
    # honeypot for admin attacks
    'admin_honeypot',
    # sign in as a user
    'loginas',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Add the automatic auth middleware just after the default
    # AuthenticationMiddleware that manages sessions and cookies
    #'djauth.middleware.AutomaticUserLoginMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # the following should be uncommented unless you are
    # embedding your apps in iframes
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# template stuff
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            '/data2/django_templates/djbootmin/',
            '/data2/django_templates/djcher/',
            '/data2/django_templates/django-djskins/',
            '/data2/livewhale/includes/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug':DEBUG,
            'context_processors': [
                'djtools.context_processors.sitevars',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# caching
'''
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 60 * 60 * 24,
        'KEY_PREFIX': 'djmapache_',
    },
}
'''
# LDAP Constants
LDAP_SERVER = ''
LDAP_SERVER_PWM = ''
LDAP_PORT = ''
LDAP_PORT_PWM = ''
LDAP_PROTOCOL = ''
LDAP_PROTOCOL_PWM = ''
LDAP_BASE = ''
LDAP_USER = ''
LDAP_PASS = ''
LDAP_EMAIL_DOMAIN = ''
LDAP_OBJECT_CLASS = ''
LDAP_OBJECT_CLASS_LIST = []
LDAP_GROUPS = {}
LDAP_RETURN = []
LDAP_RETURN_PWM = []
LDAP_ID_ATTR = ''
LDAP_CHALLENGE_ATTR = ''
LDAP_AUTH_USER_PK = False
# auth backends
AUTHENTICATION_BACKENDS = (
    'djauth.ldapBackend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LOGIN_URL = '{}accounts/login/'.format(ROOT_URL)
LOGOUT_REDIRECT_URL = '{}accounts/loggedout/'.format(ROOT_URL)
LOGIN_REDIRECT_URL = ROOT_URL
# needed for backwards compatability
LOGOUT_URL = LOGOUT_REDIRECT_URL
USE_X_FORWARDED_HOST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_DOMAIN='.carthage.edu'
SESSION_COOKIE_NAME ='django_djmapache_cookie'
SESSION_COOKIE_AGE = 86400
# SMTP settings
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_FAIL_SILENTLY = False
DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''
SERVER_MAIL = ''
REQUIRED_ATTRIBUTE = True
# logging
LOG_FILEPATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs/',
)
DEBUG_LOG_FILENAME = LOG_FILEPATH + 'debug.log'
INFO_LOG_FILENAME = LOG_FILEPATH + 'info.log'
ERROR_LOG_FILENAME = LOG_FILEPATH + 'error.log'
CUSTOM_LOG_FILENAME = LOG_FILEPATH + 'custom.log'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt': '%Y/%b/%d %H:%M:%S',
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': '%Y/%b/%d %H:%M:%S',
        },
        'custom': {
            'format': '%(asctime)s: %(levelname)s: %(message)s',
            'datefmt': '%m/%d/%Y %I:%M:%S %p',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'custom_logfile': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': CUSTOM_LOG_FILENAME,
            'formatter': 'custom',
        },
        'info_logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'backupCount': 10,
            'maxBytes': 50000,
            'filters': ['require_debug_false'],
            'filename': INFO_LOG_FILENAME,
            'formatter': 'simple',
        },
        'debug_logfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': DEBUG_LOG_FILENAME,
            'formatter': 'verbose',
        },
        'error_logfile': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': ERROR_LOG_FILENAME,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'include_html': True,
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'djmapache': {
            'handlers': ['debug_logfile'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'error_logger': {
            'handlers': ['error_logfile'],
            'level': 'ERROR',
        },
        'info_logger': {
            'handlers': ['info_logfile'],
            'level': 'INFO',
        },
        'debug_logger': {
            'handlers': ['debug_logfile'],
            # 'filters': ['require_debug_true'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
# PacketFence Apps
PACKETFENCE_API_EARL = ''
PACKETFENCE_USERNAME = ''
PACKETFENCE_PASSWORD = ''
PACKETFENCE_LOGIN_ENDPOINT = ''
PACKETFENCE_REPORTS_ENDPOINT = ''
PACKETFENCE_IP4LOGS_ENDPOINT = ''
PACKETFENCE_NODE_ENDPOINT = ''
# Handshake Application
HANDSHAKE_CSV_OUTPUT = ''
HANDSHAKE_CSV_ARCHIVED = ''
HANDSHAKE_TO_EMAIL = []
HANDSHAKE_FROM_EMAIL = ''
HANDSHAKE_ACCESS_KEY = ''
HANDSHAKE_SECRET = ''
HANDSHAKE_BUCKET = ''
HANDSHAKE_S3_FOLDER = ''
# scripsafe
#
# external scripsafe server
SCRIP_SAFE_XTRNL_SERVER = ''
SCRIP_SAFE_XTRNL_USER = ''
SCRIP_SAFE_XTRNL_KEY = '{0}/scripsafe_rsa'.format(BASE_DIR)
# server on which our transcrip reside
SCRIP_SAFE_LOCAL_SERVER = ''
SCRIP_SAFE_LOCAL_USER = ''
SCRIP_SAFE_LOCAL_KEY = '{0}/carsu_rsa'.format(BASE_DIR)
SCRIP_SAFE_LOCAL_SPOOL = ''
SCRIP_SAFE_LOCAL_BACKUP = ''
SCRIP_SAFE_LOCAL_PATH = ''
# transcrip file names start with 'cfa'
SCRIP_SAFE_FILE_PREFIX = 'cfa'
# SFTP connection dictionaries
SCRIP_SAFE_XTRNL_CONNECTION = {
    'host': SCRIP_SAFE_XTRNL_SERVER,
    'username': SCRIP_SAFE_XTRNL_USER,
    'private_key': SCRIP_SAFE_XTRNL_KEY,
}
SCRIP_SAFE_LOCAL_CONNECTION = {
    'host': SCRIP_SAFE_LOCAL_SERVER,
    'username': SCRIP_SAFE_LOCAL_USER,
    'private_key': SCRIP_SAFE_LOCAL_KEY,
}
# pdf settings
SCRIP_SAFE_FONT_SIZE = 7.5
SCRIPT_SAFE_LEADING = 10
SCRIP_SAFE_RIGHT_MARGIN = 0.25
SCRIP_SAFE_LEFT_MARGIN = 0.075
SCRIP_SAFE_TOP_MARGIN = 0.40
SCRIP_SAFE_BOTTOM_MARGIN = 0.40
# Terradotta
TERRADOTTA_HOST = ''
TERRADOTTA_USER = ''
TERRADOTTA_PKEY = ''
TERRADOTTA_PASS = ''
TERRADOTTA_CSV_OUTPUT = ''
# oclc
# external oclc server
OCLC_XTRNL_SRVR = ''
OCLC_XTRNL_USER = ''
OCLC_XTRNL_PASS = ''
OCLC_XTRNL_PATH = ''
OCLC_LOCAL_PATH = ''
# SFTP connection dictionaries
OCLC_XTRNL_CONNECTION = {
    'host': OCLC_XTRNL_SRVR,
    'username': OCLC_XTRNL_USER,
    'password': OCLC_XTRNL_PASS,
}
# oclc
OCLC_TO_EMAIL = []
OCLC_FROM_EMAIL = ''
OCLC_GROUPINDEX_LIST_INDEX = 12
# external oclc server
OCLC_ENSXTRNL_SRVR = ''
OCLC_ENSXTRNL_USER = ''
OCLC_ENSXTRNL_PASS = ''
OCLC_ENSXTRNL_PATH = ''
OCLC_ENSLOCAL_PATH = ''
# SFTP connection dictionaries
OCLC_ENSXTRNL_CONNECTION = {
    'host': OCLC_ENSXTRNL_SRVR,
    'username': OCLC_ENSXTRNL_USER,
    'password': OCLC_ENSXTRNL_PASS,
}
# Barnes and Noble AIP
BARNESNOBLE_AIP_HOST = ''
BARNESNOBLE_AIP_USER = ''
BARNESNOBLE_AIP_PORT = ''
BARNESNOBLE_AIP_HOME = ''
BARNESNOBLE_AIP_DATA = ''
BARNESNOBLE_AIP_KEY = ''
# Barnes and Noble 1
BARNESNOBLE1_HOST = ''
BARNESNOBLE1_USER = ''
BARNESNOBLE1_PKEY = ''
BARNESNOBLE1_PASS = ''
BARNESNOBLE1_PORT = 0
# Barnes and Noble 2
BARNESNOBLE2_HOST = ''
BARNESNOBLE2_USER = ''
BARNESNOBLE2_PKEY = ''
BARNESNOBLE2_PASS = ''
BARNESNOBLE2_PORT = 0
#
BARNESNOBLE_CSV_OUTPUT = ''
BARNESNOBLE_CSV_ARCHIVED = ''
BARNESNOBLE_TO_EMAIL = []
BARNESNOBLE_FROM_EMAIL = ''
# Package Concierge
CONCIERGE_HOST = ''
CONCIERGE_USER = ''
CONCIERGE_PASS = ''
CONCIERGE_PORT = 0
CONCIERGE_CSV_OUTPUT = ''
CONCIERGE_CSV_ARCHIVED = ''
CONCIERGE_TO_EMAIL = []
CONCIERGE_FROM_EMAIL = ''
# maxient
MAXIENT_HOST = ''
MAXIENT_USER = ''
MAXIENT_PKEY = ''
MAXIENT_PASS = ''
MAXIENT_CSV_OUTPUT = ''
MAXIENT_TO_EMAIL = []
MAXIENT_FROM_EMAIL = ''
MAXIENT_HEADERS = [
    'Carthage ID',
    'Username',
    'Last Name',
    'First Name',
    'Middle Name',
    'Date of Birth',
    'Gender',
    'Ethnicity',
    'Building',
    'Room Number',
    'Local Mailing Address',
    'Local City',
    'Local State',
    'Local Zip',
    'Local Phone',
    'Cell Phone',
    'Permanent Address',
    'Permanent City',
    'Permanent State',
    'Permanent Zip',
    'Permanent Country',
    'Permanent Phone',
    'Emergency Contact',
    'Email Address',
    'Classification',
    'Academic Major',
    'Academic Advisor',
    'GPA Recent',
    'GPA Cumulative',
    'Athlete',
    'Greek',
    'Honors',
    'ROTC Vet',
    'Last Update',
]
# Everbridge
EVERBRIDGE_HOST = ''
EVERBRIDGE_USER = ''
EVERBRIDGE_PKEY = ''
EVERBRIDGE_CSV_OUTPUT = ''
EVERBRIDGE_TO_EMAIL = []
EVERBRIDGE_FROM_EMAIL = ''
EVERBRIDGE_FACSTAFF_HEADERS = [
    'First Name',
    'Middle Initial',
    'Last Name',
    'Suffix',
    'External ID',
    'Country',
    'Business Name',
    'Record Type',
    'Phone 1',
    'Phone Country 1',
    'Phone 2',
    'Phone Country 2',
    'Email Address 1',
    'Email Address 2',
    'SMS 1',
    'SMS 1 Country',
    'Custom Field 1',
    'Custom Value 1',
    'Custom Field 2',
    'Custom Value 2',
    'Custom Field 3',
    'Custom Value 3',
    'END',
]
EVERBRIDGE_STUDENT_HEADERS = [
    'First Name',
    'Middle Initial',
    'Last Name',
    'Suffix',
    'External ID',
    'Country',
    'Business Name',
    'Record Type',
    'Phone 1',
    'Phone Country 1',
    'Email Address 1',
    'Email Address 2',
    'SMS 1',
    'SMS 1 Country',
    'Custom Field 1',
    'Custom Value 1',
    'Custom Field 2',
    'Custom Value 2',
    'Custom Field 3',
    'Custom Value 3',
    'END',
]
# Papercut
PAPERCUT_CSV_OUTPUT = ''
PAPERCUT_CSV_ARCHIVED = ''
PAPERCUT_TO_EMAIL = []
PAPERCUT_FROM_EMAIL = ''
PAPERCUT_BCC_EMAIL = ''
# Common Application
COMMONAPP_HOST = ''
COMMONAPP_USER = ''
COMMONAPP_PKEY = ''
COMMONAPP_PASS = ''
COMMONAPP_CSV_OUTPUT = ''
COMMONAPP_CSV_ARCHIVED = ''
COMMONAPP_TO_EMAIL = []
COMMONAPP_FROM_EMAIL = ''
# OrgSync
ORGSYNC_HOST = ''
ORGSYNC_USER = ''
ORGSYNC_PKEY = ''
ORGSYNC_PASS = ''
ORGSYNC_CSV_OUTPUT = ''
ORGSYNC_TO_EMAIL = []
ORGSYNC_FROM_EMAIL = ''
# Wing API
INDAHAUS_API_EARL = ''
INDAHAUS_USERNAME = ''
INDAHAUS_PASSWORD = ''
INDAHAUS_ENDPOINT_LOGIN = ''
INDAHAUS_ENDPOINT_LOGOUT = ''
INDAHAUS_ENDPOINT_STATS = ''
INDAHAUS_ENDPOINT_STATS_WIRELESS = ''
INDAHAUS_ENDPOINT_STATS_WIRELESS_CLIENTS = ''
INDAHAUS_XCLUDE = []
INDAHAUS_RF_DOMAINS = ()
