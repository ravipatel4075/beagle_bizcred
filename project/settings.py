"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ovwq7)mbd^y4pq0yvxss#)zn0m78r9w=m(eicr)sskh*(im(xs'

# SECURITY WARNING: don't run with debug turned on in productions
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.0.20', '219.91.133.101']
# ALLOWED_HOSTS = ['localhost', '127.0.0.1', '168.138.114.166', 'innovations.veloce.market']

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oauth2_provider',
    'bizcred.apps.BizCredConfig',
    'corsheaders'
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, 'bizcred/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend'
)

WSGI_APPLICATION = 'project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bizcred_innovation1',
        'USER': 'postgres',
        'PASSWORD': 'VeloceInnov002',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

CORS_ORIGIN_ALLOW_ALL = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

LOGIN_URL = "/accounts/login/"

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'zpropop.logix.in'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'isha@veloceinnovations.tech'
# EMAIL_HOST_PASSWORD = 'Isha%Vel@06'

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
# EMAIL_HOST_USER = 'lemon12ka4@gmail.com'
# EMAIL_HOST_PASSWORD = 'Lemon@609'
# ADMIN_EMAILS = ['cs@velocefintech.com']
EMAIL_HOST_USER = 'beaglebazaar@gmail.com'
EMAIL_HOST_PASSWORD = 'pgaxdpplnopmxtne'
ADMIN_EMAILS = ['beaglebazaar@gmail.com']

SMS_API_URL = 'http://2factor.in/API/V1/30db5222-af03-11ea-9fa5-0200cd936042/ADDON_SERVICES/SEND/TSMS'
# SMS_API_URL = 'http://2factor.in/API/V1/73e82aba-3ad5-11ec-a13b-0200cd936042/ADDON_SERVICES/SEND/TSMS'

ALLOW_ALL = True

# Setting for crif generate or Not
CRIF_GEN = True

# CRIF api for individual test
# STAG 1
# CRIF_STAG_API_1 = 'https://test.crifhighmark.com/Inquiry/do.getSecureService/DTC/initiate'
# # STAG 2
# CRIF_STAG_API_2 = 'https://test.crifhighmark.com/Inquiry/do.getSecureService/DTC/response'
# # STAG 3
# CRIF_STAG_API_3 = 'https://test.crifhighmark.com/Inquiry/do.getSecureService/DTC/response'

# CREDENTIALS For individual test
# USER_ID = 'chm_uat@veloce.com'
# PASSWORD = 'F8633BFF1D55E60BCE0B94495578779B9C881E3A'
# CUSTOMER ID
# MERCHANT_ID = 'DTC0000081'
# CUSTOMER_NAME = 'VELOCE FINTECH PVT LTD'
# APP_ID = 'BU#bif@wt&tcbP$'


# CRIF api for individual Production / Live
# STAG 1
CRIF_STAG_API_1 = 'https://cir.crifhighmark.com/Inquiry/do.getSecureService/DTC/initiate'
# STAG 2
CRIF_STAG_API_2 = 'https://cir.crifhighmark.com/Inquiry/do.getSecureService/DTC/response'
# STAG 3
CRIF_STAG_API_3 = 'https://cir.crifhighmark.com/Inquiry/do.getSecureService/DTC/response'

# CREDENTIALS For individual Production / Live
USER_ID = 'chm_prod@veloce.com'
PASSWORD = '1F84022DCFF4DD6D2A649ABB6AF6DC7663C63B7F'
# CUSTOMER ID
MERCHANT_ID = 'DTC0000110'
CUSTOMER_NAME = 'VELOCE FINTECH PVT LTD'
APP_ID = 'dq#BiT@vT%rfpB^'


# # CRIF test Credentials for commercial report
# COM_USER_ID = 'chm_uat@veloce1.com'
# COM_PASSWORD = 'E1084A985C3534F4BD2FD0FFD6F53C32BD94C46F'
# COM_MERCHANT_ID = 'DTC0000081'
# COM_CUSTOMER_NAME = 'VELOCE FINTECH PVT LTD'
# COM_APP_ID = 'cQ^$6F!&pS1#uz@@T!*J!@bT*'
#
# # CRIF api for test commercial
# # STAG 1
# CRIF_COM_STAG_API_1 = 'https://test.crifhighmark.com/BBC/comm/1'
# # STAG 2
# CRIF_COM_STAG_API_2 = 'https://test.crifhighmark.com/BBC/comm/2'
# # STAG 3
# CRIF_COM_STAG_API_3 = 'https://test.crifhighmark.com/BBC/comm/3'


# CRIF production Credentials for commercial report
COM_USER_ID = 'chm_prod@veloce1.com'
COM_PASSWORD = '7148CA61D794BA013986389B1B47F7CC7DFFEEF5'
COM_MERCHANT_ID = 'DTC0000110'
COM_CUSTOMER_NAME = 'VELOCE FINTECH PVT LTD'
# COM_APP_ID = 'cQ^$6F!&pS1#uz@@T!*J!@bT*'

# CRIF api for production commercial
# STAG 1
CRIF_COM_STAG_API_1 = 'https://cir.crifhighmark.com/BBC/comm/1'
# STAG 2
CRIF_COM_STAG_API_2 = 'https://cir.crifhighmark.com/BBC/comm/2'
# STAG 3
CRIF_COM_STAG_API_3 = 'https://cir.crifhighmark.com/BBC/comm/3'


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# secure proxy SSL header and secure cookies
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True

# session expire at browser close
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# wsgi scheme
# os.environ['wsgi.url_scheme'] = 'https'
