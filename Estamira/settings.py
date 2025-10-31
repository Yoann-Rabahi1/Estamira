

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1(57p8xlcgj3u80p7fy8i$t_@6kjefco_n1bnd7^qx(v*4+4rd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Appli',
    'authUser',
    'import_export',
    'crispy_forms',
    'mathfilters',
    'taggit',
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

ROOT_URLCONF = 'Estamira.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Estamira.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# settings.py
AUTH_USER_MODEL = 'authUser.User'

LOGIN_URL = "/auth/login/"
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = "/"


# settings.py

# Configuration du Backend d'Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Paramètres du Serveur SMTP Brevo
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# Vos identifiants Brevo
EMAIL_HOST_USER="94ab94001@smtp-brevo.com"
EMAIL_HOST_PASSWORD='SmH9wY2hXFP01MOD'
DEFAULT_FROM_EMAIL="rabahiyoann@gmail.com" # Email expéditeur par défaut



JAZZMIN_SETTINGS = {
    "site_title": "Estamira Admin",
    "site_header": "Estamira Dashboard",
    "site_brand": "Estamira",
    "welcome_sign": "Bienvenue sur Estamira",
    "copyright": "© 2025 Estamira",
    "show_ui_builder": True,  # pour tester en live les couleurs / styles
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Site Public", "url": "/", "new_window": True},
    ],
    "icons": {
        "auth.User": "fas fa-user",             # icône utilisateur
        "appli.Logement": "fas fa-home",        # icône logement
        "appli.Chauffeur": "fas fa-car",        # icône chauffeur
        "appli.Pack": "fas fa-box-open",        # icône pack
        "appli.Activite": "fas fa-futbol",      # icône activité
        "appli.Image": "fas fa-image",          # icône image
        "appli.ReservationPack": "fas fa-ticket-alt",
        "appli.ReservationChauffeur": "fas fa-taxi",
        "appli.ReservationLogement": "fas fa-bed",
    },
    "topmenu_custom_links": {
        "Elba": [
            {"name": "Reservations", "url": "/admin/appli/reservationpack/", "icon": "fas fa-ticket-alt"},
            {"name": "Logements", "url": "/admin/appli/logement/", "icon": "fas fa-home"},
            {"name": "Chauffeurs", "url": "/admin/appli/chauffeur/", "icon": "fas fa-car"},
        ]
    },
    "related_modal_active": True,  # pour ouvrir les FK dans un modal
}

JAZZMIN_UI_TWEAKS = {
    "theme": "cosmo",
    "dark_mode_theme": None,
    "navbar": "navbar-dark bg-primary",
    "sidebar": "sidebar-dark-primary",
    "button_classes": {
        "primary": "btn btn-primary",
        "secondary": "btn btn-secondary",
        "danger": "btn btn-danger",
        "success": "btn btn-success",
    },
    "form_size": "form-control-sm",
    "body_small_text": False,
}