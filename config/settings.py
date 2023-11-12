import os
from datetime import timedelta
from pathlib import Path

import environ
import sentry_sdk

BASE_DIR = Path(__file__).resolve().parent.parent

# READING ENV
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env.str("SECRET_KEY")

DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ["https://ebb.uicgroup.tech", "https://ebb.uicgroup.tech"]

INSTALLED_APPS = [
                     'django.contrib.admin',
                     'django.contrib.auth',
                     'django.contrib.contenttypes',
                     'django.contrib.sessions',
                     'django.contrib.messages',
                     'django.contrib.staticfiles',
                 ] + [
                     "apps.vehicle",
                     "apps.accounts",
                     "apps.payment",
                     "apps.charge_point",
                     "apps.core"
                 ] + [
                     "jazzmin",
                     "modeltranslation",
                     "drf_yasg",
                     "sorl.thumbnail",
                     "rest_framework",
                     'rest_framework_simplejwt',
                     'phonenumber_field',
                     'django_celery_beat',
                     "django_celery_results"
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
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


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=15),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(days=15),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=15),
}


LANGUAGE_CODE = "en-en"

LANGUAGES = [
    ("en", "English"),
    ("ru", "Русский"),
    ("uz", "Uzbek"),
]


MODELTRANSLATION_DEFAULT_LANGUAGE = "ru"


WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

PAYMENT_HOST = "zty.projects.uz"
PAYMENT_USES_SSL = True  # set the True value if you are using the SSL
PAYMENT_MODEL = "uicpayment.Transaction"
PAYMENT_VARIANTS = {
    "click": (
        "uicpayment.providers.ClickProvider",
        {"merchant_id": 22413, "merchant_service_id": 29967, "merchant_user_id": 35759, "secret_key": "OqteAcB2TN"},
    )
}

PROVIDERS = {
    "paylov": {
        "callback_url": "https://my.paylov.uz/checkout/create",
        "merchant_id": "d377c20f-56c4-4603-8566-18a3c24f7d54",
        "api_key": "DXBvBXEH.kwyH0wUu9uF9MEawaWUULE9ohuc5ZkeM",
        "username": "Paylov",
        "password": "[$kF[ggIHSmu2k#t,Yj2.blTs7dSSGeo",
    },
    "payme": {
        "callback_url": "https://checkout.paycom.uz",
        "merchant_id": "64fee17236ef51a083e4567c",
        "secret_key": "IWNyJdISwD76UfSmWrD@hpKseQsVI1ghh6?x",
        "test_secret_key": "GxhVJbuMQkrMBeX@HMoP7nI%uT8kMnpC3sIK",
    },
}

DATABASES = {
    "default": {
        "ENGINE": env.str("DB_ENGINE"),
        "NAME": env.str("DB_NAME"),
        "USER": env.str("DB_USER"),
        "PASSWORD": env.get_value("DB_PASSWORD"),
        "HOST": env.str("DB_HOST"),
        "PORT": env.str("DB_PORT"),
        "ATOMIC_REQUESTS": True,
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        # 'django.contrib.auth.backends.ModelBackend',
    ),
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 12,
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

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


PUSH_NOTIFICATIONS_SETTINGS = {
    "USER_MODEL": "apps.accounts.User",
    "FCM_API_KEY": "AAAAZWIWVj8:APA91bF-JuDqk_g72mPfL4x93JG_-5SI2-Bwg82yCNgMisgGPA9Gkdtl5WN_iSqPPnr1EMKhNeUA_eXfQ3m_JOWOLxXA-63TrJ3ZGLjxuyJL2AKqHAOByjrulOQ490hGBs9A5ziDFLUs",
}

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True
USE_TZ = True


STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"{env.str('REDIS_URL', 'redis://localhost:6379/0')}",
        "KEY_PREFIX": "ebb-charger-app",
    }
}

# CELERY CONFIGURATION
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", "redis://localhost:6379")
CELERY_RESULT_BACKEND = env.str("CELERY_BROKER_URL", "redis://localhost:6379")

CELERY_TIMEZONE = "Asia/Tashkent"

CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    "daily-user-gift-check": {
        "task": "accounts.tasks.daily_user_gift_check",
    },
    "daily-transaction-report": {
        "task": "apps.charge_point.tasks.daily_transaction_report",
    },
    "daily-transaction-report-charge-point": {
        "task": "apps.charge_point.tasks.daily_transaction_report_charge_point",
    },
    "history-transaction-report": {
        "task": "apps.charge_point.tasks.history_transaction_report_charge_point",
    },
}

ONE_SIGNAL_APP_ID = "16b4f3a9-69cb-4fad-8cce-c71fb2c15b83"
ONE_SIGNAL_REST_API_KEY = "ZDY5OGEzYzYtMzZiMC00OGZjLWEzMGQtZDA5MDMzZjhiN2Fm"

sentry_sdk.init(
    dsn="https://d4ed84678280c48f78b02d06a096c394@o713327.ingest.sentry.io/4506081013071872",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)
