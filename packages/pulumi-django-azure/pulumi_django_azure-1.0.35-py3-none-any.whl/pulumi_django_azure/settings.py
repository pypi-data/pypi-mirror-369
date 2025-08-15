import environ
from azure.keyvault.secrets import SecretClient

from .azure_helper import AZURE_CREDENTIAL, LOCAL_IP_ADDRESSES, get_db_password, get_subscription

env = environ.Env()

SECRET_KEY = env("DJANGO_SECRET_KEY", default=None)

IS_AZURE_ENVIRONMENT = env("IS_AZURE_ENVIRONMENT", default=False)

# Some generic stuff we only need if we're running in Azure.
# Most of the other stuff will check for the explicit variable we need.
if IS_AZURE_ENVIRONMENT:
    # Detect HTTPS behind AppService
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Azure context
    AZURE_SUBSCRIPTION = get_subscription()
    AZURE_TENANT_ID = AZURE_SUBSCRIPTION.tenant_id
    AZURE_SUBSCRIPTION_ID = AZURE_SUBSCRIPTION.subscription_id

# Health check path
HEALTH_CHECK_PATH = env("HEALTH_CHECK_PATH", default="/health")

ALLOWED_HOSTS: list = env.list("DJANGO_ALLOWED_HOSTS", default=[])

# WEBSITE_HOSTNAME contains the Azure domain name
if website_hostname := env("WEBSITE_HOSTNAME", default=None):
    ALLOWED_HOSTS.append(website_hostname)

# Add the local IP addresses of the machine for health checks
ALLOWED_HOSTS.extend(LOCAL_IP_ADDRESSES)

# Azure Key Vault
if azure_key_vault := env("AZURE_KEY_VAULT", default=None):
    AZURE_KEY_VAULT_URI = f"https://{azure_key_vault}.vault.azure.net"
    AZURE_KEY_VAULT_CLIENT = SecretClient(vault_url=AZURE_KEY_VAULT_URI, credential=AZURE_CREDENTIAL)

# Allow CSRF cookies to be sent from our domains
# CSRF_TRUSTED_ORIGINS = ["https://" + host for host in ALLOWED_HOSTS]
if azure_storage_account_name := env("AZURE_STORAGE_ACCOUNT_NAME", default=None):
    AZURE_ACCOUNT_NAME = azure_storage_account_name
    AZURE_TOKEN_CREDENTIAL = AZURE_CREDENTIAL


# CDN domain - shared for all storages
if cdn_host := env("CDN_HOST", default=None):
    AZURE_CUSTOM_DOMAIN = cdn_host

    STATIC_URL = f"https://{AZURE_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AZURE_CUSTOM_DOMAIN}/media/"

# Storage configuration
STORAGES = {}
if container_media := env("AZURE_STORAGE_CONTAINER_MEDIA", default=None):
    STORAGES["default"] = {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "azure_container": container_media,
            "overwrite_files": False,
        },
    }

if container_staticfiles := env("AZURE_STORAGE_CONTAINER_STATICFILES", default=None):
    STORAGES["staticfiles"] = {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "azure_container": container_staticfiles,
        },
    }

# This setting enables password rotation in the health check middleware
if IS_AZURE_ENVIRONMENT:
    AZURE_DB_PASSWORD = True
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "HOST": env("DB_HOST"),
            "PASSWORD": get_db_password(),
            "PORT": "5432",
            "OPTIONS": {
                "sslmode": "require",
            },
            # Make connections persistent
            "CONN_MAX_AGE": None,
            # To enable health checks, add the following:
            # "CONN_HEALTH_CHECKS": True,
        }
    }

# Email
EMAIL_BACKEND = "django_azure_communication_email.EmailBackend"
AZURE_COMMUNICATION_ENDPOINT = env("AZURE_COMMUNICATION_SERVICE_ENDPOINT", default=None)
DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL", default=None)


# Logging
if IS_AZURE_ENVIRONMENT:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "timestamped": {
                "format": "{asctime} {levelname} [p:{process:d}] [t:{thread:d}] {message}",
                "style": "{",
            },
        },
        "handlers": {
            "file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "/home/LogFiles/django.log",
                # 50 MB
                "maxBytes": 52428800,
                "backupCount": 5,
                "formatter": "timestamped",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["file"],
                "level": "INFO",
                "propagate": True,
            },
            "pulumi_django_azure": {
                "handlers": ["file"],
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }

# Redis, if enabled
REDIS_SIDECAR = env("REDIS_SIDECAR", default=False)

if REDIS_SIDECAR:
    # This will prevent the website from failing if Redis is not available.
    DJANGO_REDIS_IGNORE_EXCEPTIONS = True
    DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://localhost:6379/0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PARSER_CLASS": "redis.connection._HiredisParser",
            },
        },
    }
