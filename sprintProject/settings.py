import os
from dotenv import load_dotenv, find_dotenv

from pathlib import Path

load_dotenv(find_dotenv())

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Приложение проекта
    'fstr_app',

    # Добавленные библиотеки
    'rest_framework', 'django_filters', 'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sprintProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR / 'static'

WSGI_APPLICATION = 'sprintProject.wsgi.application'

# Настройки для PostqreSQL
DATABASES = {
    # Настройки при использовании SQLite
    'default':
        {'ENGINE': 'django.db.backends.sqlite3',
         'NAME': BASE_DIR / 'db.sqlite'}

    # Настройки при использовании PostqreSQL
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'HOST': os.getenv('FSTR_DB_HOST'),
    #     'PORT': os.getenv('FSTR_DB_PORT'),
    #     'NAME': os.getenv('FSTR_DB_NAME'),
    #     'USER': os.getenv('FSTR_DB_LOGIN'),
    #     'PASSWORD': os.getenv('FSTR_DB_PASS'),
    # }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки по REST
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    # ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'FTSR API - service',
    'DESCRIPTION': 'API для работы с БД федерации спорт туризма',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # Включить автоматическое использование docstring
    'PREPROCESSING_HOOKS': [
        'drf_spectacular.hooks.preprocess_exclude_path_format',
    ],
    'APPEND_COMPONENTS': {
        'schemas': {
            'ExampleComponent': {
                'description': 'Автоматическое описание из docstring',
            }
        }
    },
    # Настройки Swagger UI
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': False,
        'displayOperationId': False,  # Показывать ID операции
        'displayRequestDuration': False,
    },
    # Автоматически использовать docstring из view-классов
    'SCHEMA_PATH_PREFIX': r'/api/',
    'SCHEMA_COERCE_PATH_PK': True,
}