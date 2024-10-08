"""
Django settings for ompedis_project project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from django.contrib.messages import constants as messages

# Configuración para el almacenamiento de mensajes en sesión
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Opcional: Configurar clases CSS para los diferentes niveles de mensajes (bootstrap)
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración rápida para desarrollo - no se debe usar en producción
# Verifica: https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/
SECRET_KEY = 'django-insecure-b_%(9=h18+-wgb+rcrw_jib6sb1ll@=(-$nho9%b@of6*d!3@t'  # Clave secreta, debe mantenerse segura

# Configuración de depuración: debería ser False en producción para mayor seguridad
DEBUG = True

# Lista de hosts permitidos para acceder al proyecto (usar '*' permite todos los hosts, no recomendado para producción)
ALLOWED_HOSTS = ['*']

# Aplicaciones instaladas en el proyecto
INSTALLED_APPS = [
    'django.contrib.admin',  # Admin site
    'django.contrib.auth',  # Sistema de autenticación
    'django.contrib.contenttypes',  # Tipos de contenido (framework para manejar modelos)
    'django.contrib.sessions',  # Manejo de sesiones en el sitio
    'django.contrib.messages',  # Mensajes del sistema
    'django.contrib.staticfiles',  # Archivos estáticos (CSS, JS, etc.)
    'usuarios',  # Aplicación personalizada para manejo de usuarios
    'pacientes',  # Aplicación para manejo de pacientes
    'reportes',  # Aplicación para generar reportes/estadísticas
    'crispy_forms',  # Aplicación para mejorar la apariencia de formularios
    'crispy_bootstrap4',  # Integración con Bootstrap 4 para Crispy Forms
]

# Paquete de plantillas para crispy_forms (se usará Bootstrap 4)
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Middleware: componentes que se ejecutan en cada solicitud al servidor
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Seguridad
    'django.contrib.sessions.middleware.SessionMiddleware',  # Manejo de sesiones
    'django.middleware.common.CommonMiddleware',  # Manejo común de solicitudes
    'django.middleware.csrf.CsrfViewMiddleware',  # Protección CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Autenticación de usuarios
    'django.contrib.messages.middleware.MessageMiddleware',  # Manejo de mensajes
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Protección contra clickjacking
]

# Archivo de configuración de URLs principal del proyecto
ROOT_URLCONF = 'ompedis_project.urls'

# Configuración de plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Directorio donde se almacenan las plantillas del proyecto
        'APP_DIRS': True,  # Buscar plantillas en las carpetas de cada aplicación instalada
        'OPTIONS': {
            'context_processors': [  # Procesadores de contexto utilizados en las plantillas
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Configuración para el servidor WSGI (Web Server Gateway Interface)
WSGI_APPLICATION = 'ompedis_project.wsgi.application'

# Configuración de la base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Backend para conectar con PostgreSQL
        'NAME': 'ompedis2',  # Nombre de la base de datos
        'USER': 'postgres',  # Usuario para la conexión a la base de datos
        'PASSWORD': 'manager',  # Contraseña del usuario (debe mantenerse segura)
        'HOST': 'localhost',  # Dirección del servidor de la base de datos
        'PORT': '5432',  # Puerto predeterminado para PostgreSQL
    }
}

# Validación de contraseñas (para asegurar contraseñas seguras)
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

# Configuración de la internacionalización
LANGUAGE_CODE = 'es'  # Idioma predeterminado (español)
TIME_ZONE = 'UTC'  # Zona horaria
USE_I18N = True  # Habilitar la internacionalización
USE_TZ = True  # Usar la zona horaria definida
DATE_INPUT_FORMATS = ['%d/%m/%Y', '%Y-%m-%d']  # Formatos aceptados para fechas

# URL para el login (dónde se redirige si no se está autenticado)
LOGIN_URL = '/usuarios/login/'

# Configuración de archivos estáticos (CSS, JavaScript, Imágenes)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # Directorios donde se almacenan los archivos estáticos

# Configuración de tipo de campo de clave primaria predeterminado para modelos
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'usuarios.CustomUser'

# Configuración del backend de correo electrónico para enviar emails desde la aplicación
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Servidor SMTP de Gmail
EMAIL_PORT = 587  # Puerto de conexión
EMAIL_USE_TLS = True  # Utilizar TLS para la conexión
EMAIL_HOST_USER = 'lcayaxp@miumg.edu.gt'  # Correo electrónico que envía los emails
EMAIL_HOST_PASSWORD = 'hafr duhd jlue avgm'  # Contraseña del correo electrónico (debería mantenerse segura)
