import logging
from django.apps import apps
from django.db import connections
import re

logger = logging.getLogger(__name__)

def _should_log_info():
    """Check if info logging should be enabled based on settings"""
    from ..settings import get_setting
    return not get_setting('DISABLE_INFO_LOGGING', False)

def _should_log_warning():
    """Check if warning logging should be enabled based on settings"""
    from ..settings import get_setting
    return not get_setting('DISABLE_INFO_LOGGING', False)

def _should_log_debug():
    """Check if debug logging should be enabled based on settings"""
    from ..settings import get_setting
    return not get_setting('DISABLE_INFO_LOGGING', False)

def _should_log_error():
    """Check if error logging should be enabled based on settings"""
    from ..settings import get_setting
    return not get_setting('DISABLE_INFO_LOGGING', False)

def log_info(message):
    """Log info message only if info logging is enabled"""
    if _should_log_info():
        log_info(message)

def log_warning(message):
    """Log warning message only if warning logging is enabled"""
    if _should_log_warning():
        log_warning(message)

def log_debug(message):
    """Log debug message only if debug logging is enabled"""
    if _should_log_debug():
        log_debug(message)

def log_error(message):
    """Log error message only if error logging is enabled"""
    if _should_log_error():
        log_error(message)

def detect_table_case_mismatches(database_alias='default'):
    """
    Detect table name case mismatches between Django models and database tables.
    
    Returns:
        dict: Dictionary with mismatches found
    """
    mismatches = {}
    
    try:
        # Get existing tables from database
        connection = connections[database_alias]
        existing_tables = connection.introspection.table_names()
        table_lower_map = {table.lower(): table for table in existing_tables}
        
        # Check each model
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                expected_table = model._meta.db_table
                expected_lower = expected_table.lower()
                
                # Check if table exists with different case
                if expected_lower in table_lower_map:
                    actual_name = table_lower_map[expected_lower]
                    if actual_name != expected_table:
                        model_key = f"{model._meta.app_label}.{model.__name__}"
                        mismatches[model_key] = {
                            'model': model,
                            'expected_table': expected_table,
                            'actual_table': actual_name,
                            'type': 'case_mismatch'
                        }
        
        return mismatches
        
    except Exception as e:
        log_error(f"Error detecting table case mismatches: {e}")
        return {}

def report_table_case_mismatches(database_alias='default'):
    """
    Print a report of table name case mismatches.
    """
    from ..settings import get_setting
    
    mismatches = detect_table_case_mismatches(database_alias)
    debug_mode = get_setting('DEBUG_MODE')
    disable_info = get_setting('DISABLE_INFO_LOGGING', False)
    
    if not mismatches:
        if not disable_info:
            print("✅ No table name case mismatches found.")
        return
    
    if debug_mode:
        print(f"⚠️  Found {len(mismatches)} table name case mismatch(es):")
        print("=" * 60)
        
        for model_key, info in mismatches.items():
            print(f"Model: {model_key}")
            print(f"  Expected table: '{info['expected_table']}'")
            print(f"  Actual table:   '{info['actual_table']}'")
            print(f"  Type: {info['type']}")
            print()
        
        print("💡 To fix these mismatches, run:")
        print(f"   python manage.py dbsync --database={database_alias}")
        print("   (The tool will prompt for each rename operation)")

def detect_table_name_conflicts(database_alias='default'):
    """
    Detect table name conflicts where both lowercase and uppercase versions exist.
    
    Returns:
        dict: Dictionary with conflicts found
    """
    conflicts = {}
    
    try:
        # Get existing tables from database
        connection = connections[database_alias]
        existing_tables = connection.introspection.table_names()
        
        # Create case-insensitive mapping
        table_lower_map = {}
        for table in existing_tables:
            table_lower = table.lower()
            if table_lower in table_lower_map:
                # Found a conflict - both lowercase and uppercase versions exist
                conflicts[table_lower] = {
                    'tables': [table_lower_map[table_lower], table],
                    'type': 'case_conflict'
                }
            else:
                table_lower_map[table_lower] = table
        
        return conflicts
        
    except Exception as e:
        log_error(f"Error detecting table name conflicts: {e}")
        return {}

def report_table_name_conflicts(database_alias='default'):
    """
    Print a report of table name conflicts.
    """
    from ..settings import get_setting
    
    conflicts = detect_table_name_conflicts(database_alias)
    debug_mode = get_setting('DEBUG_MODE')
    disable_info = get_setting('DISABLE_INFO_LOGGING', False)
    
    if not conflicts:
        if not disable_info:
            print("✅ No table name conflicts found.")
        return
    
    if debug_mode:
        print(f"⚠️  Found {len(conflicts)} table name conflict(s):")
        print("=" * 60)
        
        for table_lower, info in conflicts.items():
            print(f"Conflict for table name: '{table_lower}'")
            print(f"  Existing tables: {info['tables']}")
            print(f"  Type: {info['type']}")
            print()
        
        print("💡 These conflicts can cause issues with table renaming.")
        print("   Consider manually resolving the conflicts before running dbsync.")

def generate_model_from_table(table_name, table_info, database_alias='default'):
    """
    Generate a Django model from a database table structure.
    
    Args:
        table_name: Name of the table
        table_info: Dictionary with table information (columns, constraints, etc.)
        database_alias: Database alias to use
    
    Returns:
        str: Generated Django model code
    """
    try:
        from django.db import connections
        connection = connections[database_alias]
        
        # Get table structure
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = cursor.fetchall()
        
        # Generate model code
        model_code = f"""class {table_name.title().replace('_', '')}(models.Model):
    \"\"\"
    Auto-generated model for table '{table_name}'
    Generated by django-dbsync
    Powerd By Love Dazzell
    \"\"\"
"""
        
        # Map MySQL types to Django fields
        type_mapping = {
            'int': 'models.IntegerField',
            'bigint': 'models.BigIntegerField',
            'smallint': 'models.SmallIntegerField',
            'tinyint': 'models.SmallIntegerField',
            'varchar': 'models.CharField',
            'char': 'models.CharField',
            'text': 'models.TextField',
            'longtext': 'models.TextField',
            'mediumtext': 'models.TextField',
            'datetime': 'models.DateTimeField',
            'timestamp': 'models.DateTimeField',
            'date': 'models.DateField',
            'time': 'models.TimeField',
            'decimal': 'models.DecimalField',
            'float': 'models.FloatField',
            'double': 'models.FloatField',
            'boolean': 'models.BooleanField',
            'json': 'models.JSONField',
            'uuid': 'models.UUIDField',
        }
        
        # Process each column
        for column in columns:
            col_name, col_type, null_ok, key, default, extra = column
            
            # Skip primary key if it's auto-increment
            if key == 'PRI' and extra == 'auto_increment':
                continue
            
            # Parse column type
            base_type = col_type.split('(')[0].lower()
            django_field = type_mapping.get(base_type, 'models.CharField')
            
            # Build field parameters
            params = []
            
            # Handle max_length for char fields
            if base_type in ['varchar', 'char']:
                length_match = re.search(r'\((\d+)\)', col_type)
                if length_match:
                    params.append(f"max_length={length_match.group(1)}")
            
            # Handle null/blank
            if null_ok == 'YES':
                params.append("null=True")
                params.append("blank=True")
            else:
                params.append("null=False")
                params.append("blank=False")
            
            # Handle default values
            if default is not None and default != 'NULL':
                if base_type in ['int', 'bigint', 'smallint', 'tinyint']:
                    params.append(f"default={default}")
                elif base_type in ['varchar', 'char', 'text']:
                    params.append(f"default='{default}'")
                elif base_type in ['datetime', 'timestamp']:
                    # Handle datetime defaults properly
                    if default.upper() == 'CURRENT_TIMESTAMP':
                        params.append("auto_now_add=True")
                    elif default.upper() == 'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP':
                        params.append("auto_now=True")
                    else:
                        # For other datetime defaults, use the raw value
                        params.append(f"default='{default}'")
                else:
                    params.append(f"default={default}")
            
            # Handle unique constraint
            if key == 'UNI':
                params.append("unique=True")
            
            # Build the field line
            field_params = ', '.join(params) if params else ''
            field_line = f"    {col_name} = {django_field}({field_params})"
            
            model_code += field_line + "\n"
        
        # Add Meta class
        model_code += f"""
    class Meta:
        db_table = '{table_name}'
        managed = False  # Django won't manage this table

    def __str__(self):
        return f'{table_name.title().replace('_', '')}(id={{self.id}})'
"""
        
        return model_code
        
    except Exception as e:
        return f"# Error generating model for {table_name}: {e}"


def generate_orphaned_models_report(orphaned_tables, database_alias='default', output_dir=None):
    """
    Generate Django models for orphaned tables and save to file.
    
    Args:
        orphaned_tables: List of orphaned table dictionaries
        database_alias: Database alias to use
        output_dir: Directory to save the report (default: dbsync_reports/)
    
    Returns:
        str: Path to the generated file
    """
    import os
    from datetime import datetime
    from ..settings import get_setting
    
    if not orphaned_tables:
        return None
    
    # Create output directory
    if output_dir is None:
        output_dir = get_setting('REPORT_OUTPUT_DIR', 'dbsync_reports/')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"orphaned_models_{timestamp}.py"
    filepath = os.path.join(output_dir, filename)
    
    # Generate the report content
    report_content = f"""# Django Models for Orphaned Tables
# Generated by django-dbsync on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 
# Instructions:
# 1. Copy the models you want to keep to your Django app's models.py
# 2. Remove the 'managed = False' line if you want Django to manage the table
# 3. Update the Meta class as needed
# 4. Run 'python manage.py makemigrations' and 'python manage.py migrate'

from django.db import models

"""
    
    # Generate models for each orphaned table
    for table in orphaned_tables:
        table_name = table['name']
        report_content += f"# Table: {table_name}\n"
        report_content += f"# Rows: {table.get('rows', 0)}, Size: {table.get('size_mb', 0)} MB\n"
        
        # Get table info from database
        try:
            from django.db import connections
            connection = connections[database_alias]
            cursor = connection.cursor()
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            
            table_info = {
                'columns': columns,
                'rows': table.get('rows', 0),
                'size_mb': table.get('size_mb', 0)
            }
            
            model_code = generate_model_from_table(table_name, table_info, database_alias)
            report_content += model_code + "\n\n"
            
        except Exception as e:
            report_content += f"# Error getting table structure: {e}\n\n"
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return filepath

def list_database_views(database_alias='default', names_only=False):
    """
    List all views in the database for the given alias.
    If names_only=True, returns (count, [names])
    Otherwise, returns a list of dicts: [{name: ..., columns: [...]}, ...]
    """
    from django.db import connections
    connection = connections[database_alias]
    engine = connection.vendor
    views = []
    cursor = connection.cursor()
    if engine == 'mysql':
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
        for row in cursor.fetchall():
            view_name = row[0]
            cursor.execute(f"DESCRIBE `{view_name}`")
            columns = [col[0] for col in cursor.fetchall()]
            views.append({'name': view_name, 'columns': columns})
    elif engine == 'postgresql':
        cursor.execute("""
            SELECT table_name FROM information_schema.views
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        """)
        for row in cursor.fetchall():
            view_name = row[0]
            cursor.execute(f'SELECT * FROM "{view_name}" LIMIT 0')
            columns = [desc[0] for desc in cursor.description]
            views.append({'name': view_name, 'columns': columns})
    elif engine == 'sqlite':
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        for row in cursor.fetchall():
            view_name = row[0]
            cursor.execute(f'PRAGMA table_info("{view_name}")')
            columns = [col[1] for col in cursor.fetchall()]
            views.append({'name': view_name, 'columns': columns})
    if names_only:
        return len(views), [v['name'] for v in views]
    return views

def generate_model_for_view(view_name, columns, database_alias='default'):
    """
    Generate a Django model for a database view.
    """
    class_name = view_name.title().replace('_', '')
    model_code = f"class {class_name}(models.Model):\n"
    model_code += f"    \"\"\"\n    Auto-generated model for view '{view_name}'\n    Generated by django-dbsync\n    Powerd By Love Dazzell\n    \"\"\"\n"
    for col in columns:
        model_code += f"    {col} = models.TextField(blank=True, null=True)\n"
    model_code += f"\n    class Meta:\n        db_table = '{view_name}'\n        managed = False  # Django won't manage this view\n\n    def __str__(self):\n        return '{class_name}()'\n"
    return model_code

def generate_views_report(database_alias='default', output_dir=None):
    """
    Generate a report and Django models for all database views.
    """
    import os
    from datetime import datetime
    from ..settings import get_setting
    views = list_database_views(database_alias)
    if not views:
        return None
    if output_dir is None:
        output_dir = get_setting('REPORT_OUTPUT_DIR', 'dbsync_reports/')
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"db_views_{timestamp}.py"
    filepath = os.path.join(output_dir, filename)
    report_content = f"""# Django Models for Database Views\n# Generated by django-dbsync on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n# Powerd By Love Dazzell\n#\n# Instructions:\n# 1. Copy the models you want to keep to your Django app's models.py\n# 2. Remove the 'managed = False' line if you want Django to manage the view\n# 3. Update the Meta class as needed\n#\nfrom django.db import models\n\n"""
    for view in views:
        report_content += f"# View: {view['name']}\n"
        report_content += generate_model_for_view(view['name'], view['columns'], database_alias) + "\n\n"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_content)
    return filepath, views
