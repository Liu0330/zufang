"""
Django settings for zufang project.

Generated by 'django-admin startproject' using Django 2.2.10.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'edrnuun9k1^2j0extzeb-%mgh6zizvhdqr)zskz0xvgz2l8b&b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'debug_toolbar',
    'rest_framework_swagger',
    'django_filters',
    'common',
    'api',
    'backend',
    'django_celery_results',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.co'
    'mmon.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zufang.urls'

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

WSGI_APPLICATION = 'zufang.wsgi.application'

# djangorestframework的配置
REST_FRAMEWORK = {
    #添加接口文档api/docs页面
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    # 配置默认页面大小
    'PAGE_SIZE': 5,
    # 配置默认的分页类
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PAGINATION_CLASS': 'api.helpers.CustomPagePagination',
    # # 配置默认的过滤和排序类
    # 'DEFAULT_FILTER_BACKENDS': (
    #     'django_filters.rest_framework.DjangoFilterBackend',
    #     'rest_framework.filters.OrderingFilter',
    # ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        # 'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/min',
        # 'user': '10000/day'
    }
}

# # 调试工具栏
DEBUG_TOOLBAR_CONFIG = {
    # 引入jquery库
    'JQUERY_URL': 'https://cdn.bootcss.com/jquery/3.4.1/jquery.min.js',
    # 工具栏是否折叠
    'SHOW_COLLAPSED': True,
    # 是否显示工具栏
    'SHOW_TOOLBAR_CALLBACK': lambda x: True,
}

# # 配置允许跨域访问接口数据
# CORS_ORIGIN_ALLOW_ALL = True
#
# # 跨域访问允许的请求头
# CORS_ALLOW_HEADERS = (
#     'accept',
#     'accept-encoding',
#     'authorization',
#     'content-type',
#     'dnt',
#     'origin',
#     'user-agent',
#     'x-csrftoken',
#     'x-requested-with',
#     'token',
# )

# # 跨域访问支持的HTTP请求方法
# CORS_ALLOW_METHODS = (
#     'DELETE',
#     'GET',
#     'OPTIONS',
#     'PATCH',
#     'POST',
#     'PUT',
# )

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zufang',
        'HOST': '121.36.92.49',
        'PORT': 3306,
        'USER': 'liu',
        'PASSWORD': 'liuwang',
        'CHARSET': 'utf8'
    },

    'backend': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hrs',
        'HOST': '121.36.92.49',
        'PORT': 3306,
        'USER': 'liu',
        'PASSWORD': 'liuwang',
        'CHARSET': 'utf8',
        'TIME_ZONE': 'Asia/Shanghai',
    }

}

# # 数据库路由配置
# DATABASE_ROUTERS = []

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': [
            # 'redis://121.36.92.49:6379/0',
            'redis://127.0.0.1:6379/0',
        ],
        'KEY_PREFIX': 'zufang',#前缀
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 2048,#提前建好，空间换时间，池化技术
            },
        }
    },
}


# 数据库路由配置
DATABASE_ROUTERS = [
    'common.db_routers.MultiDbRouter',
    # 'common.db_routers.MasterSlaveRouter',
]

# 会话相关配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# SESSION_CACHE_ALIAS = 'session'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Chongqing'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# # 日志配置（日志级别越低内容越详细）
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'simple': {
#             'format': '%(asctime)s %(module)s.%(funcName)s: %(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#         },
#         'verbose': {
#             'format': '%(asctime)s %(levelname)s [%(process)d-%(threadName)s] '
#                       '%(module)s.%(funcName)s line %(lineno)d: %(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#         }
#     },
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#     },
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'filters': ['require_debug_true'],
#             'formatter': 'simple',
#             'level': 'DEBUG',
#         },
#         'file1': {
#             'class': 'logging.handlers.TimedRotatingFileHandler',
#             'filename': 'access.log',
#             'when': 'W0',
#             'backupCount': 12,
#             'formatter': 'simple',
#             'level': 'INFO',
#         },
#         'file2': {
#             'class': 'logging.handlers.TimedRotatingFileHandler',
#             'filename': 'error.log',
#             'when': 'D',
#             'backupCount': 31,
#             'formatter': 'verbose',
#             'level': 'WARNING',
#         },
#     },
#     'loggers': {
#         'django.db': {
#             'handlers': ['console', 'file1', 'file2'],
#             'propagate': True,
#             'level': 'DEBUG',
#         },
#     }
# }

# # 保持HTTPS连接的时间
# SECURE_HSTS_SECONDS = 3600
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# # 自动重定向到安全连接
# SECURE_SSL_REDIRECT = True

# # 避免浏览器自作聪明推断内容类型（避免跨站脚本攻击风险）
# SECURE_CONTENT_TYPE_NOSNIFF = True

# # 避免跨站脚本攻击
# SECURE_BROWSER_XSS_FILTER = True

# # COOKIE只能通过HTTPS进行传输
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# # 防止点击劫持攻击手段（不允许使用<iframe>标签进行加载）
# X_FRAME_OPTIONS = 'DENY'
