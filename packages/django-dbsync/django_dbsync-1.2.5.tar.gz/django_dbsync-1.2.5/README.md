# Django DB Sync

**Django DB Sync** is a powerful, intelligent database synchronization tool designed specifically for Django projects. It automatically detects and resolves schema differences between your Django models and database tables, eliminating the need for manual migrations in many scenarios.

## What's New

### Latest Improvements (v1.2.4)

#### 🐛 Bug Fixes
- **Enhanced Foreign Key Error Reporting**: Fixed generic "Could not fully fix foreign key column" warnings to now show the actual database error details, making debugging much easier
- **Unique Constraints Synchronization**: Fixed bug where unique constraints were not being properly removed from the database when models didn't specify them, now constraints are synchronized independently of column alterations

#### ✨ Enhanced Features
- **Better Error Messages**: Foreign key constraint failures now display the real database error instead of generic messages
- **Improved Debugging**: More detailed error information for constraint operations
- **Better User Experience**: Clearer feedback when operations fail, helping users understand exactly what went wrong

---

## Why Django DB Sync?

Unlike Django's built-in migrations system, Django DB Sync works by analyzing the current state of your database and comparing it directly with your Django models. This approach is particularly valuable when:

- Working with legacy databases that weren't created with Django
- Dealing with databases that have been manually modified
- Syncing schemas across different environments
- Cleaning up orphaned tables and unused columns
- Requiring granular control over database schema changes

## Key Features

- Multi-Database Support: Works seamlessly with MySQL, PostgreSQL, SQLite, and Oracle
- Intelligent Schema Detection: Automatically compares Django models with actual database schema
- Safety First: Built-in dry-run mode and backup creation before making changes
- Comprehensive Reporting: Detailed HTML reports and colored terminal output
- Orphaned Table Management: Identifies and manages tables without corresponding Django models
- Database Views Management: List and generate models for database views
- Smart Field Mapping: Intelligent mapping between Django field types and database column types
- Constraint Handling: Proper management of foreign keys, indexes, and other constraints
- Beautiful Interface: Colored terminal output with progress indicators and status updates

## 🛠️ Core Capabilities

1. **Table Management**: Create, rename, and manage database tables
2. **Column Operations**: Add, modify, and remove columns with proper type mapping
3. **Constraint Handling**: Manage foreign keys, unique constraints, and indexes
4. **Data Preservation**: Safely modify schemas while preserving existing data
5. **Backup Integration**: Automatic backup creation before destructive operations
6. **Detailed Reporting**: Comprehensive logs and HTML reports of all operations
7. **Views Management**: List and generate Django models for database views
8. **Orphaned Table Management**: Generate Django models for orphaned tables

## 🔧 Technical Highlights

- **Database Agnostic**: Works with all major database backends supported by Django
- **Type-Safe Operations**: Intelligent field type mapping and validation
- **Transaction Safety**: All operations wrapped in database transactions
- **Extensible Architecture**: Modular design for easy customization and extension
- **Production Ready**: Thoroughly tested with comprehensive error handling

## Installation

```bash
pip install django-dbsync
```

Add to your Django settings:

```python
INSTALLED_APPS = [
    # ... other apps
    'django_dbsync',
]

# Optional: Configure django-dbsync
DJANGO_DBSYNC = {
    'DEFAULT_DATABASE': 'default',
    'AUTO_CREATE_TABLES': True,
    'AUTO_ADD_COLUMNS': True,
    'AUTO_DROP_COLUMNS': False,
    'EXCLUDE_APPS': ['admin', 'contenttypes', 'sessions'],
    'COLORED_OUTPUT': True,
    'SHOW_ORPHANED_TABLES': True,
}
```

## Usage

### Basic Sync Commands
```bash
# Basic sync commands
python manage.py dbsync  # Sync default database
python manage.py dbsync --database=secondary  # Sync specific database
python manage.py dbsync --dry-run  # Show changes without applying
python manage.py dbsync --auto-approve  # Auto-approve all changes (dangerous!)
python manage.py dbsync --drop-orphaned  # Drop orphaned tables (dangerous!)
python manage.py dbsync --no-restriction  # Include all models (including Django built-ins)
```

### App and Table Filtering
```bash
# App management
python manage.py dbsync --exclude-apps admin auth contenttypes sessions  # Exclude specific apps
python manage.py dbsync --include-apps myapp otherapp  # Include only specific apps
python manage.py dbsync --exclude-app-patterns ".*_test"  # Exclude apps matching pattern

# Table filtering
python manage.py dbsync --exclude-table-patterns ".*_log" ".*_temp"  # Exclude tables matching patterns
```

### Backup and Reporting
```bash
# Backup and reporting
python manage.py dbsync --backup  # Create backup before sync
python manage.py dbsync --report json  # Generate JSON report
python manage.py dbsync --report html  # Generate HTML report
python manage.py dbsync --report both  # Generate both JSON and HTML reports
```

### Safety and Manual Commands
```bash
# Safety checks
python manage.py dbsync --drop-orphaned --dry-run  # Check what would be dropped
python manage.py dbsync --suggest-manual-commands  # Show manual SQL commands
python manage.py dbsync --show-orphaned  # Show orphaned tables without dropping
```

### Orphaned Table Management
```bash
# Show orphaned tables
python manage.py dbsync --show-orphaned

# Drop orphaned tables (use with caution!)
python manage.py dbsync --drop-orphaned

# Generate Django models for orphaned tables
python manage.py dbsync --generate-orphaned-models
```



### Database Views Management
```bash
# Views management (NEW!)
python manage.py dbsync --list-views  # List all database views
python manage.py dbsync --report-views  # Generate report and models for all views
```

### Retry Mechanism
```bash
# Retry mechanism for failed operations
python manage.py dbsync --retry-failed  # Retry failed operations up to 3 times
python manage.py dbsync --retry-failed --max-retries 5  # Set custom retry attempts
python manage.py dbsync -rf -mr 5  # Using shortcuts
```

### Output Control
```bash
# Output control
python manage.py dbsync --verbosity 2  # Increase verbosity (0-3)
python manage.py dbsync --no-color  # Disable colored output
python manage.py dbsync --force-color  # Force colored output
```

### Information Commands
```bash
# Information commands
python manage.py dbsync --help  # Show help
python manage.py dbsync --version  # Show version
```

### Database Check Commands
```bash
# Database checking commands
python manage.py dbcheck  # Check database schema
python manage.py dbcheck --database=secondary  # Check specific database
python manage.py dbcheck --table=my_table  # Show specific table details
python manage.py dbcheck --compare-models  # Compare with Django models
python manage.py dbcheck --check-case-mismatches  # Check for case mismatches
python manage.py dbcheck --check-name-conflicts  # Check for name conflicts
python manage.py dbcheck --verbose  # Show detailed information
python manage.py dbcheck --fix  # Attempt to fix issues automatically
python manage.py dbcheck --include-apps=app1,app2  # Check specific apps only
python manage.py dbcheck --include-tables=table1,table2  # Check specific tables only
```

## Database Views Management

Django-dbsync now supports managing database views! This is particularly useful when working with:

- Read-only views for reporting
- Complex queries that need to be materialized as views
- Legacy databases with existing views
- Analytics and data warehouse scenarios

### Listing Database Views

To see all views in your database:

```bash
python manage.py dbsync --list-views
```

**Example Output:**
```
Django Database Sync v1.1.6
==================================================

Database Views:
- user_summary (2 columns)
- sales_report (5 columns)
- active_users (3 columns)

Views operation completed!
```

### Generating Models for Views

To generate Django models for all database views:

```bash
python manage.py dbsync --report-views
```

This creates a Python file with Django models for all views:

```python
# Django Models for Database Views
# Generated by django-dbsync on 2025-07-30 10:34:31
# 
# Instructions:
# 1. Copy the models you want to keep to your Django app's models.py
# 2. These models use 'managed = False' by default (Django won't manage the views)
# 3. Views are read-only by default
# 4. Update the Meta class as needed

from django.db import models

# View: user_summary
class UserSummary(models.Model):
    """
    Auto-generated model for view 'user_summary'
    Generated by django-dbsync
    """
    user_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=150)
    total_orders = models.IntegerField()

    class Meta:
        db_table = 'user_summary'
        managed = False  # Django won't manage this view

    def __str__(self):
        return f'UserSummary(user_id={self.user_id})'
```

**Benefits:**
- **Easy integration**: Use views as Django models
- **Read-only by default**: Safe for reporting and analytics
- **Auto-generated**: No manual model writing needed
- **Complete**: Includes all field types and constraints

### Handling Invalid Views

If your database contains invalid views (e.g., views that reference non-existent tables), the tool will:

1. **Show an error message** indicating which view is invalid
2. **Continue processing** other views
3. **Complete the operation** with a summary

**Example error handling:**
```
❌ Error listing views: (1356, "View 'test.publisher_summary' references invalid table(s) or column(s) or function(s) or definer/invoker of view lack rights to use them")
Views operation completed!
```

**To fix invalid views:**
```sql
-- Drop the invalid view
DROP VIEW IF EXISTS publisher_summary;

-- Or recreate it with correct references
CREATE VIEW publisher_summary AS 
SELECT name, website FROM publisher;
```

## Retry Mechanism

Django-dbsync includes a robust retry mechanism that automatically retries failed operations, particularly useful for handling temporary database issues, connection problems, or constraint conflicts.

### How It Works

The retry mechanism automatically retries failed operations up to a configurable number of attempts (default: 3). This is especially helpful for:

- **Foreign Key Operations**: When creating foreign key constraints that depend on tables being created first
- **Many-to-Many Tables**: When creating intermediate tables for M2M relationships
- **Database Locks**: When operations fail due to temporary database locks
- **Connection Issues**: When database connections are temporarily unavailable
- **Constraint Conflicts**: When operations fail due to timing issues with constraints

### Basic Usage

Enable retry mechanism with default settings:

```bash
python manage.py dbsync --retry-failed
```

**Example Output:**
```
🔄 Retry mechanism enabled - will retry failed operations up to 3 times
Starting synchronization...

Sync Results:
------------------------------
✅ core.User
✅ core.Profile

✅ All operations completed successfully after retry!
Synchronization completed!
```

### Custom Retry Attempts

Set a custom number of retry attempts:

```bash
python manage.py dbsync --retry-failed --max-retries 5
# Or using shortcuts:
python manage.py dbsync -rf -mr 5
```

### Retry Results Display

When operations fail even after retries, you'll see detailed information:

```
Failed Operations After Retry:
----------------------------------------
❌ FOREIGN_KEY on core_profile
   Attempts: 3
   Error: (1452, "Cannot add or update a child row: a foreign key constraint fails")

❌ MANY_TO_MANY on core_user_groups
   Attempts: 3
   Error: (1215, "Cannot add foreign key constraint")

⚠️  These operations failed after maximum retry attempts
💡 Consider fixing the underlying issues and running the sync again
```

### When Retry Mechanism is Useful

1. **Complex Model Dependencies**: When models have complex foreign key relationships
2. **Large Databases**: When syncing large databases with many constraints
3. **Production Environments**: When dealing with database locks or temporary issues
4. **Multi-User Scenarios**: When other processes might be modifying the database
5. **Network Instability**: When database connections are occasionally unstable

### Best Practices

1. **Use with Dry Run**: Test with dry run first to see what might fail
   ```bash
   python manage.py dbsync --dry-run --retry-failed
   ```

2. **Monitor Retry Results**: Check the retry results to identify persistent issues
3. **Fix Underlying Issues**: Address the root causes of failed operations
4. **Use Appropriate Retry Count**: Don't set retry attempts too high (3-5 is usually sufficient)

### Configuration

You can also configure retry settings in your Django settings:

```python
DJANGO_DBSYNC = {
    'RETRY_FAILED_OPERATIONS': True,  # Enable retry mechanism
    'MAX_RETRY_ATTEMPTS': 3,          # Default retry attempts
}
```

### Retry Logic

The retry mechanism uses intelligent retry logic:

1. **Exponential Backoff**: Waits progressively longer between retries
2. **Operation-Specific**: Different retry strategies for different operation types
3. **Constraint-Aware**: Understands foreign key and constraint dependencies
4. **Safe Retries**: Only retries operations that are safe to retry
5. **Detailed Logging**: Provides comprehensive information about retry attempts

### Troubleshooting

If operations consistently fail after retries:

1. **Check Database Logs**: Look for database-specific error messages
2. **Verify Constraints**: Ensure all referenced tables and columns exist
3. **Check Permissions**: Verify database user has necessary permissions
4. **Review Dependencies**: Check if model relationships are correctly defined
5. **Manual Investigation**: Use `--dry-run` to see exactly what operations are failing

## Configuration

### Database Settings

Support for multiple databases: 

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'main_db',
        'USER': 'user',
        'PASSWORD': 'pass',
        'HOST': 'localhost',
    },
    'analytics': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'analytics_db',
        'USER': 'user',
        'PASSWORD': 'pass',
        'HOST': 'localhost',
    }
}

# Sync configuration per database
DJANGO_DBSYNC = {
    'CUSTOM_DATABASES': {
        'analytics': {
            'AUTO_DROP_COLUMNS': True,
            'EXCLUDE_APPS': ['admin'],
        }
    }
}
```

### Complete Settings Reference

```python
DJANGO_DBSYNC = {
    # Database configuration
    'DEFAULT_DATABASE': 'default',
    'CUSTOM_DATABASES': None,
    
    # Sync behavior
    'AUTO_CREATE_TABLES': True,
    'AUTO_ADD_COLUMNS': True,
    'AUTO_DROP_COLUMNS': False,
    'AUTO_RENAME_TABLES': False,
    'AUTO_FIX_TABLE_CASE': True,  # Automatically fix table name case mismatches
    'BACKUP_BEFORE_SYNC': True,
        
    # Safety settings
    'EXCLUDE_APPS': ['sessions', 'admin', 'contenttypes'],
    'EXCLUDE_TABLES': [],
    'DRY_RUN_MODE': False,
    
    # Report settings
    'GENERATE_HTML_REPORT': False,
    'REPORT_OUTPUT_DIR': 'dbsync_reports/',
    'SHOW_ORPHANED_TABLES': True,
}
```

## Supported Field Types

All Django field types are supported across MySQL, PostgreSQL, and SQLite:

- AutoField, BigAutoField
- CharField, TextField, EmailField, URLField, SlugField
- IntegerField, BigIntegerField, SmallIntegerField
- PositiveIntegerField, PositiveSmallIntegerField
- FloatField, DecimalField
- BooleanField
- DateField, DateTimeField, TimeField
- UUIDField, JSONField
- FileField, ImageField
- ForeignKey, OneToOneField, ManyToManyField

## Table Name Case Handling

Django-dbsync automatically detects and handles table name case mismatches between your Django models and the database. This is common when:

- Your model has `db_table = 'abcd'` but the database table is `ABCD`
- Database systems are case-insensitive but Django models use specific casing
- Tables were created with different naming conventions

### Automatic Case Fixing

By default, the tool will automatically fix case-only mismatches (when `AUTO_FIX_TABLE_CASE = True`):

```bash
# The tool will automatically rename 'ABCD' to 'abcd'
python manage.py dbsync
```

### Manual Control

To disable automatic case fixing and get prompted for each rename:

```python
DJANGO_DBSYNC = {
    'AUTO_FIX_TABLE_CASE': False,
}
```

### Checking for Case Mismatches

To check for table name case mismatches without fixing them:

```bash
python manage.py dbcheck --check-case-mismatches
```

This will show you all mismatches found and provide guidance on how to fix them.

### Manual SQL Commands for Table Renames

When table name conflicts are detected, you can get manual SQL commands to resolve them:

```bash
python manage.py dbsync --dry-run --suggest-manual-commands
```

This will show you the exact SQL commands needed to rename tables manually:

```
============================================================
🔧 MANUAL SQL COMMANDS FOR TABLE RENAMES
============================================================
The following SQL commands can be run manually to rename tables:

1. MySQL case-insensitive conflict resolution: 'publisher_detail2' → 'Publisher_detail2'
   SQL: RENAME TABLE `publisher_detail2` TO `Publisher_detail2`;

💡 Instructions:
   1. Connect to your database using your preferred SQL client
   2. Run the commands above one by one
   3. Run 'python manage.py dbsync' again to complete the sync
   4. Make sure to backup your database before running these commands!
```

This gives you full control over table renaming operations while ensuring data safety.

**Note:** Manual SQL commands are automatically displayed in dry-run mode, so you don't need the `--suggest-manual-commands` flag anymore.

### Generating Models for Orphaned Tables

When orphaned tables are found, you can generate Django models for them:

```bash
python manage.py dbsync --generate-orphaned-models
```

This creates a Python file with Django models for all orphaned tables:

```python
# Django Models for Orphaned Tables
# Generated by django-dbsync on 2025-07-30 10:34:31
# 
# Instructions:
# 1. Copy the models you want to keep to your Django app's models.py
# 2. Remove the 'managed = False' line if you want Django to manage the table
# 3. Update the Meta class as needed
# 4. Run 'python manage.py makemigrations' and 'python manage.py migrate'

from django.db import models

# Table: Publisher
# Rows: 0, Size: 0.11 MB
class Publisher(models.Model):
    """
    Auto-generated model for table 'Publisher'
    Generated by django-dbsync
    """
    status = models.SmallIntegerField(null=False, blank=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)  # Properly mapped from CURRENT_TIMESTAMP
    updated_at = models.DateTimeField(auto_now=True)  # Properly mapped from CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        db_table = 'publisher'
        managed = False  # Django won't manage this table

    def __str__(self):
        return f'Publisher(id={self.id})'
```

**Benefits:**
- **Easy retention**: Copy models to keep orphaned tables
- **Auto-generated**: No manual model writing needed
- **Safe**: Uses `managed = False` by default
- **Complete**: Includes all field types and constraints
- **Smart defaults**: Properly maps `CURRENT_TIMESTAMP` to `auto_now_add=True` and `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` to `auto_now=True`

### Table Name Conflicts

Sometimes databases can have both lowercase and uppercase versions of the same table name (e.g., `publisher` and `Publisher`). This can cause issues with table renaming operations.

To check for table name conflicts:

```bash
python manage.py dbcheck --check-name-conflicts
```

This will identify any tables that have case conflicts and provide guidance on how to resolve them.

**Example conflict scenario:**
- Database has both `publisher` and `Publisher` tables
- Django model expects `Publisher` 
- The tool will detect this conflict and avoid the rename operation
- You'll need to manually resolve the conflict before syncing

## Example Output

### Basic Sync Output
```
Django Database Sync v1.1.6
==================================================
Starting synchronization...

Sync Results:
------------------------------
✅ core.User

✅ No orphaned tables found!
Synchronization completed!
```

### Views Management Output
```
Django Database Sync v1.1.6
==================================================

Database Views:
- user_summary (2 columns)
- sales_report (5 columns)
- active_users (3 columns)

Views operation completed!
```

### Orphaned Tables Output
```
⚠️  Orphaned Tables (1 found):
----------------------------------------
🗃️  lead - 0 rows, 0.11 MB
```

### Report Generation Output
```
HTML report: dbsync_reports/dbsync_report_20250730_094915.html
JSON report: dbsync_reports/dbsync_report_20250730_094923.json
```

## Command Status Summary

### ✅ Working Commands
- `--help` - Shows comprehensive help with all available options
- `--version` - Displays version number
- `--dry-run` - Shows what would be done without making changes
- `--auto-approve` - Works correctly with dry-run mode
- `--database` - Correctly specifies database alias
- `--exclude-apps` - Successfully excludes Django built-in apps
- `--include-apps` - Successfully includes only specified app models
- `--no-restriction` - Includes all models including Django built-ins
- `--exclude-table-patterns` - Correctly excludes tables matching pattern
- `--show-orphaned` - Shows orphaned tables
- `--generate-orphaned-models` - Generates models for orphaned tables
- `--report html` - Generates HTML report file successfully
- `--report json` - Generates JSON report file successfully
- `--suggest-manual-commands` - Works with dry-run mode
- `--list-views` - Lists database views (works after fixing invalid views)
- `--report-views` - Generates report and models for views
- `--backup` - Creates backup successfully (works after fixing invalid views)
- `--retry-failed` - Retries failed operations with intelligent retry logic
- `--max-retries` - Configures custom retry attempt count
- `--verbosity` - Works correctly
- `--no-color` - Removes colorization from output
- All `dbcheck` commands - Work correctly for database checking

### ⚠️ Known Issues
- **Invalid Database Views**: If your database contains invalid views (referencing non-existent tables), the `--list-views` and `--backup` commands will show error messages but still complete successfully
- **Solution**: Drop or fix invalid views using SQL commands

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

- Documentation: https://lovedazzell.in
- Email: lovepreetdazzell@gmail.com
