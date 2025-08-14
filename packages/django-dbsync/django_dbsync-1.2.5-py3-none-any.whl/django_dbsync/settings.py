from django.conf import settings
from . import __version__

# Default settings for django-dbsync
DBSYNC_SETTINGS = {
    # Version
    'VERSION': __version__,
    # Database configuration
    'DEFAULT_DATABASE': 'default',
    'CUSTOM_DATABASES': None,  # Can override in settings
    
    # Sync behavior
    'AUTO_CREATE_TABLES': True,
    'AUTO_ADD_COLUMNS': True,
    'AUTO_DROP_COLUMNS': False,  # Always ask by default
    'AUTO_RENAME_TABLES': False,  # Always ask by default
    'AUTO_FIX_TABLE_CASE': True,  # Automatically fix table name case mismatches
    'BACKUP_BEFORE_SYNC': True,
    
    # Output settings
    'COLORED_OUTPUT': True,
    'VERBOSE_LOGGING': True,
    'SHOW_PROGRESS': True,

    'DEBUG_MODE': False,  # Enable debug mode to show debug statements
    'DISABLE_INFO_LOGGING': True,  # Disable info-level logging when True
    
    # Safety settings
    'EXCLUDE_APPS': [],
    # 'EXCLUDE_APPS': ['contenttypes', 'auth', 'sessions', 'admin'],
    'EXCLUDE_TABLES': [],
    
    # Regex-based exclusion patterns
    'EXCLUDE_APP_PATTERNS': [],  # Regex patterns for app names
    'EXCLUDE_TABLE_PATTERNS': [],  # Regex patterns for table names
    # Example: 'EXCLUDE_TABLE_PATTERNS': [r'^vw_', r'_temp$', r'^backup_.*']
    
    'DRY_RUN_MODE': False,
    
    # Report settings
    'GENERATE_HTML_REPORT': False,
    'REPORT_OUTPUT_DIR': 'dbsync_reports/',
    'SHOW_ORPHANED_TABLES': True,
}

def get_setting(key, default=None):
    """Get django-dbsync setting with fallback to default"""
    user_settings = getattr(settings, 'DJANGO_DBSYNC', {})
    return user_settings.get(key, DBSYNC_SETTINGS.get(key, default))
