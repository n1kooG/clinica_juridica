from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'cambia-esta-clave-en-produccion'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.gestion',
    'apps.cuentas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.gestion.signals.AuditoriaMiddleware',
    'apps.gestion.middleware.XSSProtectionMiddleware',
    'apps.gestion.middleware.SecurityHeadersMiddleware',
    'apps.gestion.session_middleware.SessionTimeoutMiddleware',
    'apps.gestion.session_middleware.SessionSecurityMiddleware',
]

# =============================================================================
# GESTIÓN DE SESIONES - ISO/IEC 27001 A.9.4.2
# =============================================================================

# Motor de sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Tiempo de expiración de sesión inactiva (30 minutos)
SESSION_COOKIE_AGE = 1800  # 30 minutos en segundos

# Expirar sesión al cerrar navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Guardar sesión en cada request (actualiza last_activity)
SESSION_SAVE_EVERY_REQUEST = True

# Configuración de cookies de sesión (seguridad)
SESSION_COOKIE_HTTPONLY = True  # No accesible desde JavaScript
SESSION_COOKIE_SECURE = False   # True en producción (HTTPS)
SESSION_COOKIE_SAMESITE = 'Lax'  # Protección CSRF

# Nombre de la cookie de sesión
SESSION_COOKIE_NAME = 'clinica_juridica_sessionid'

ROOT_URLCONF = 'clinica_juridica.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.gestion.permissions.permisos_context_processor',  # Permisos en templates
            ],
        },
    },
]

WSGI_APPLICATION = 'clinica_juridica.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'apps.gestion.password_validators.PasswordStrengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'apps.gestion.password_validators.NoCommonPasswordValidator',
    },
    {
        'NAME': 'apps.gestion.password_validators.NoUserAttributeSimilarityValidator',
    },
    {
        'NAME': 'apps.gestion.password_validators.PasswordHistoryValidator',
    },
]

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# =============================================================================
# LOGGING - ISO/IEC 27001 Trazabilidad
# =============================================================================

import os

LOG_DIR = BASE_DIR / 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {module} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{asctime}] {levelname} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'seguridad': {
            'format': '[{asctime}] SEGURIDAD {levelname} | IP:{ip} | Usuario:{user} | {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
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
        # Consola (desarrollo)
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
        
        # Archivo general
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        
        # Archivo de errores
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'errors.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        
        # Archivo de seguridad
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'security.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        
        # Archivo de auditoría
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'audit.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 20,
            'formatter': 'verbose',
        },
    },
    
    'loggers': {
        # Logger de Django
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        
        # Logger de errores de Django
        'django.request': {
            'handlers': ['error_file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        
        # Logger de seguridad
        'seguridad': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Logger de auditoría
        'auditoria': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Logger de la aplicación
        'apps': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# =============================================================================
# CACHÉ - Optimización de Rendimiento
# =============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'clinica-juridica-cache',
        'TIMEOUT': 86400,  # 24 horas
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Tiempo de caché para catálogos (en segundos)
CACHE_CATALOGOS_TIMEOUT = 86400  # 24 horas
CACHE_DASHBOARD_TIMEOUT = 300     # 5 minutos