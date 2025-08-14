class DjangoDbSyncException(Exception):
    """Base exception for django-dbsync"""
    pass

class DatabaseConnectionError(DjangoDbSyncException):
    """Raised when database connection fails"""
    pass

class FieldMappingError(DjangoDbSyncException):
    """Raised when field mapping fails"""
    pass

class SyncOperationError(DjangoDbSyncException):
    """Raised when sync operation fails"""
    pass