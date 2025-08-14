from django.apps import AppConfig

class DjangoDbSyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_dbsync'
    verbose_name = 'Django Database Sync'