import logging
from django.db import models
from .exceptions import FieldMappingError
from ..settings import get_setting

logger = logging.getLogger(__name__)

def _should_log_info():
    """Check if info logging should be enabled based on settings"""
    return not get_setting('DISABLE_INFO_LOGGING', False)

def _should_log_warning():
    """Check if warning logging should be enabled based on settings"""
    return not get_setting('DISABLE_INFO_LOGGING', False)

def _should_log_debug():
    """Check if debug logging should be enabled based on settings"""
    return not get_setting('DISABLE_INFO_LOGGING', False)

def _should_log_error():
    """Check if error logging should be enabled based on settings"""
    return not get_setting('DISABLE_INFO_LOGGING', False)

def log_info(message):
    """Log info message only if info logging is enabled"""
    if _should_log_info():
        logger.info(message)

def log_warning(message):
    """Log warning message only if warning logging is enabled"""
    if _should_log_warning():
        logger.warning(message)

def log_debug(message):
    """Log debug message only if debug logging is enabled"""
    if _should_log_debug():
        logger.debug(message)

def log_error(message):
    """Log error message only if error logging is enabled"""
    if _should_log_error():
        logger.error(message)

class FieldMapper:
    """
    Map Django fields to database-specific column definitions
    
    This class provides methods to:
    - Convert Django model fields to database column definitions
    - Handle database-specific type mappings (MySQL, PostgreSQL, SQLite)
    - Manage field constraints and defaults
    - Determine table exclusion rules
    """
    
    def __init__(self, database_engine):
        """
        Initialize FieldMapper with database engine
        
        Args:
            database_engine (str): Database engine name (mysql, postgresql, sqlite)
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 FieldMapper.__init__: Initializing with database_engine='{database_engine}'")
        
        self.engine = database_engine.lower()
        self.type_mappings = self._get_type_mappings()
        
        if debug_mode:
            print(f"✅ FieldMapper.__init__: Successfully initialized for '{self.engine}' engine")
            print(f"   Available field types: {list(self.type_mappings.keys())}")
    
    def _get_type_mappings(self):
        """
        Get field type mappings for different database engines
        
        This method returns a dictionary of Django field types mapped to
        database-specific column type functions. Each function takes a field
        and returns the appropriate SQL type definition.
        
        Returns:
            dict: Dictionary mapping field types to type functions
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 FieldMapper._get_type_mappings: Getting type mappings for '{self.engine}' engine")
        
        if self.engine == 'mysql':
            mappings = self._get_mysql_mappings()
        elif self.engine == 'postgresql':
            mappings = self._get_postgresql_mappings()
        elif self.engine == 'sqlite':
            mappings = self._get_sqlite_mappings()
        else:
            error_msg = f"Unsupported database engine: {self.engine}"
            if debug_mode:
                print(f"❌ FieldMapper._get_type_mappings: {error_msg}")
            raise FieldMappingError(error_msg)
        
        if debug_mode:
            print(f"✅ FieldMapper._get_type_mappings: Loaded {len(mappings)} field type mappings")
        
        return mappings
    
    def _get_mysql_mappings(self):
        """
        MySQL field type mappings
        
        Returns a dictionary of Django field types mapped to MySQL-specific
        column type definitions. MySQL-specific features include:
        - AUTO_INCREMENT for auto fields
        - UNSIGNED for positive integer fields
        - TINYINT(1) for boolean fields
        - Specific VARCHAR lengths
        
        Returns:
            dict: MySQL-specific field type mappings
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 FieldMapper._get_mysql_mappings: Creating MySQL-specific type mappings")
        
        mappings = {
            'AutoField': lambda f: 'INT AUTO_INCREMENT',
            'BigAutoField': lambda f: 'BIGINT AUTO_INCREMENT',
            'CharField': lambda f: f'VARCHAR({getattr(f, "max_length", 255)})',
            'TextField': lambda f: 'TEXT',
            'IntegerField': lambda f: 'INT',
            'BigIntegerField': lambda f: 'BIGINT',
            'SmallIntegerField': lambda f: 'SMALLINT',
            'PositiveIntegerField': lambda f: 'INT UNSIGNED',
            'PositiveSmallIntegerField': lambda f: 'SMALLINT UNSIGNED',
            'FloatField': lambda f: 'FLOAT',
            'DecimalField': lambda f: f'DECIMAL({getattr(f, "max_digits", 10)},{getattr(f, "decimal_places", 2)})',
            'BooleanField': lambda f: 'BOOLEAN',
            'DateField': lambda f: 'DATE',
            'DateTimeField': lambda f: 'DATETIME',
            'TimeField': lambda f: 'TIME',
            'EmailField': lambda f: f'VARCHAR({getattr(f, "max_length", 254)})',
            'URLField': lambda f: f'VARCHAR({getattr(f, "max_length", 200)})',
            'SlugField': lambda f: f'VARCHAR({getattr(f, "max_length", 50)})',
            'ImageField': lambda f: f'VARCHAR({getattr(f, "max_length", 100)})',
            'FileField': lambda f: f'VARCHAR({getattr(f, "max_length", 100)})',
            'UUIDField': lambda f: 'CHAR(36)',
            'JSONField': lambda f: self._get_json_field_type(f),
            'DurationField': lambda f: 'BIGINT',  # Store as seconds
            'GenericIPAddressField': lambda f: 'VARCHAR(45)',  # IPv6 max length
            'BinaryField': lambda f: 'LONGBLOB',
            'ForeignKey': lambda f: self._get_foreign_key_type(f),
            'OneToOneField': lambda f: self._get_foreign_key_type(f),
        }
        
        if debug_mode:
            print(f"✅ FieldMapper._get_mysql_mappings: Created {len(mappings)} MySQL mappings")
        
        return mappings
    
    def _get_postgresql_mappings(self):
        """
        PostgreSQL field type mappings
        
        Returns a dictionary of Django field types mapped to PostgreSQL-specific
        column type definitions. PostgreSQL-specific features include:
        - SERIAL/BIGSERIAL for auto fields
        - JSONB for JSON fields
        - UUID type for UUID fields
        - CHECK constraints for positive fields
        
        Returns:
            dict: PostgreSQL-specific field type mappings
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 FieldMapper._get_postgresql_mappings: Creating PostgreSQL-specific type mappings")
        
        mappings = {
            'AutoField': lambda f: 'SERIAL',
            'BigAutoField': lambda f: 'BIGSERIAL',
            'CharField': lambda f: f'VARCHAR({getattr(f, "max_length", 255)})',
            'TextField': lambda f: 'TEXT',
            'IntegerField': lambda f: 'INTEGER',
            'BigIntegerField': lambda f: 'BIGINT',
            'SmallIntegerField': lambda f: 'SMALLINT',
            'PositiveIntegerField': lambda f: 'INTEGER CHECK (value >= 0)',
            'PositiveSmallIntegerField': lambda f: 'SMALLINT CHECK (value >= 0)',
            'FloatField': lambda f: 'REAL',
            'DecimalField': lambda f: f'DECIMAL({getattr(f, "max_digits", 10)},{getattr(f, "decimal_places", 2)})',
            'BooleanField': lambda f: 'BOOLEAN',
            'DateField': lambda f: 'DATE',
            'DateTimeField': lambda f: 'TIMESTAMP',
            'TimeField': lambda f: 'TIME',
            'EmailField': lambda f: f'VARCHAR({getattr(f, "max_length", 254)})',
            'URLField': lambda f: f'VARCHAR({getattr(f, "max_length", 200)})',
            'SlugField': lambda f: f'VARCHAR({getattr(f, "max_length", 50)})',
            'ImageField': lambda f: f'VARCHAR({getattr(f, "max_length", 100)})',
            'FileField': lambda f: f'VARCHAR({getattr(f, "max_length", 100)})',
            'UUIDField': lambda f: 'UUID',
            'JSONField': lambda f: 'JSONB',
            'DurationField': lambda f: 'BIGINT',  # Store as seconds
            'GenericIPAddressField': lambda f: 'VARCHAR(45)',  # IPv6 max length
            'BinaryField': lambda f: 'BYTEA',
            'ForeignKey': lambda f: self._get_foreign_key_type(f),
            'OneToOneField': lambda f: self._get_foreign_key_type(f),
        }
        
        if debug_mode:
            print(f"✅ FieldMapper._get_postgresql_mappings: Created {len(mappings)} PostgreSQL mappings")
        
        return mappings
    
    def _get_sqlite_mappings(self):
        """
        SQLite field type mappings
        
        Returns a dictionary of Django field types mapped to SQLite-specific
        column type definitions. SQLite-specific features include:
        - INTEGER PRIMARY KEY AUTOINCREMENT for auto fields
        - Simplified type system (INTEGER, REAL, TEXT, BLOB)
        - No native JSON support (uses TEXT)
        
        Returns:
            dict: SQLite-specific field type mappings
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 FieldMapper._get_sqlite_mappings: Creating SQLite-specific type mappings")
        
        mappings = {
            'AutoField': lambda f: 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'BigAutoField': lambda f: 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'CharField': lambda f: 'VARCHAR',
            'TextField': lambda f: 'TEXT',
            'IntegerField': lambda f: 'INTEGER',
            'BigIntegerField': lambda f: 'INTEGER',
            'SmallIntegerField': lambda f: 'INTEGER',
            'PositiveIntegerField': lambda f: 'INTEGER',
            'PositiveSmallIntegerField': lambda f: 'INTEGER',
            'FloatField': lambda f: 'REAL',
            'DecimalField': lambda f: 'DECIMAL',
            'BooleanField': lambda f: 'BOOLEAN',
            'DateField': lambda f: 'DATE',
            'DateTimeField': lambda f: 'DATETIME',
            'TimeField': lambda f: 'TIME',
            'EmailField': lambda f: 'VARCHAR',
            'URLField': lambda f: 'VARCHAR',
            'SlugField': lambda f: 'VARCHAR',
            'ImageField': lambda f: 'VARCHAR',
            'FileField': lambda f: 'VARCHAR',
            'UUIDField': lambda f: 'CHAR(36)',
            'JSONField': lambda f: 'TEXT',
            'DurationField': lambda f: 'INTEGER',  # Store as seconds
            'GenericIPAddressField': lambda f: 'VARCHAR(45)',  # IPv6 max length
            'BinaryField': lambda f: 'BLOB',
            'ForeignKey': lambda f: self._get_foreign_key_type(f),
            'OneToOneField': lambda f: self._get_foreign_key_type(f),
        }
        
        if debug_mode:
            print(f"✅ FieldMapper._get_sqlite_mappings: Created {len(mappings)} SQLite mappings")
        
        return mappings
    
    def should_exclude_table(self, table_name: str) -> bool:
        """
        Check if a table should be excluded from synchronization
        
        This method determines whether a table should be excluded based on:
        - Django system table prefixes (auth_, django_, etc.)
        - Explicit table exclusions from settings
        - Regex pattern exclusions
        - No-restriction mode flag
        
        Args:
            table_name (str): Name of the table to check
            
        Returns:
            bool: True if table should be excluded, False otherwise
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 FieldMapper.should_exclude_table: Checking if table '{table_name}' should be excluded")
        
        import re
        
        # If no-restriction mode is enabled, don't exclude any tables
        if hasattr(self, '_no_restriction') and self._no_restriction:
            if debug_mode:
                print(f"   No-restriction mode: not excluding table '{table_name}'")
            log_info(f"No-restriction mode: not excluding table '{table_name}'")
            return False
        
        # Check Django system table prefixes
        system_table_prefixes = [
            'auth_',
            'django_',
            'contenttypes_',
            'sessions_',
            'admin_',
        ]
        
        # Check system tables
        for prefix in system_table_prefixes:
            if table_name.startswith(prefix):
                if debug_mode:
                    print(f"   Excluding system table: {table_name} (matches prefix: {prefix})")
                log_info(f"Excluding system table: {table_name} (matches prefix: {prefix})")
                return True
        
        # Check explicit table exclusions
        exclude_tables = get_setting('EXCLUDE_TABLES', [])
        if table_name in exclude_tables:
            if debug_mode:
                print(f"   Excluding table via EXCLUDE_TABLES: {table_name}")
            log_info(f"Excluding table via EXCLUDE_TABLES: {table_name}")
            return True
        
        # Check regex pattern exclusions
        exclude_patterns = get_setting('EXCLUDE_TABLE_PATTERNS', [])
        
        # Add temporary patterns from command line if available via sync engine
        if hasattr(self, 'sync_engine') and hasattr(self.sync_engine, '_temp_exclude_table_patterns'):
            if self.sync_engine._temp_exclude_table_patterns:
                exclude_patterns.extend(self.sync_engine._temp_exclude_table_patterns)
        
        # Log all patterns being checked
        if exclude_patterns:
            if debug_mode:
                print(f"   Checking table '{table_name}' against exclusion patterns: {exclude_patterns}")
            log_info(f"Checking table '{table_name}' against exclusion patterns: {exclude_patterns}")
        
        for pattern in exclude_patterns:
            try:
                if re.match(pattern, table_name):
                    if debug_mode:
                        print(f"   Excluding table '{table_name}' (matches pattern: {pattern})")
                    log_info(f"Excluding table '{table_name}' (matches pattern: {pattern})")
                    return True
            except re.error as e:
                error_msg = f"Invalid regex pattern '{pattern}': {e}"
                if debug_mode:
                    print(f"   ⚠️ {error_msg}")
                log_warning(error_msg)
                continue
        
        if debug_mode:
            print(f"   Table '{table_name}' not excluded")
        log_info(f"Table '{table_name}' not excluded")
        return False
    
    def _get_foreign_key_type(self, field):
        """
        Get the correct data type for a foreign key column based on the referenced primary key
        
        This method determines the appropriate column type for a foreign key by:
        1. Getting the related model
        2. Finding its primary key field
        3. Mapping the primary key type to the appropriate foreign key type
        4. Handling database-specific type mappings
        
        Args:
            field: Django ForeignKey or OneToOneField instance
            
        Returns:
            str: Database column type for the foreign key
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 FieldMapper._get_foreign_key_type: Getting FK type for field '{field.name}'")
        
        try:
            # Get the related model and its primary key field
            related_model = field.related_model
            pk_field = related_model._meta.pk
            pk_field_type = type(pk_field).__name__
            
            if debug_mode:
                print(f"   Related model: {related_model.__name__}")
                print(f"   Primary key field: {pk_field.name} ({pk_field_type})")
            
            # Map the primary key field type to the appropriate foreign key column type
            if self.engine == 'mysql':
                type_mapping = {
                    'AutoField': 'INT',
                    'BigAutoField': 'BIGINT',
                    'IntegerField': 'INT',
                    'BigIntegerField': 'BIGINT',
                    'SmallIntegerField': 'SMALLINT',
                    'PositiveIntegerField': 'INT UNSIGNED',
                    'PositiveSmallIntegerField': 'SMALLINT UNSIGNED',
                    'UUIDField': 'CHAR(36)',
                }
            elif self.engine == 'postgresql':
                type_mapping = {
                    'AutoField': 'INTEGER',
                    'BigAutoField': 'BIGINT',
                    'IntegerField': 'INTEGER',
                    'BigIntegerField': 'BIGINT',
                    'SmallIntegerField': 'SMALLINT',
                    'PositiveIntegerField': 'INTEGER',
                    'PositiveSmallIntegerField': 'SMALLINT',
                    'UUIDField': 'UUID',
                }
            elif self.engine == 'sqlite':
                # SQLite uses INTEGER for all integer types
                type_mapping = {
                    'AutoField': 'INTEGER',
                    'BigAutoField': 'INTEGER',
                    'IntegerField': 'INTEGER',
                    'BigIntegerField': 'INTEGER',
                    'SmallIntegerField': 'INTEGER',
                    'PositiveIntegerField': 'INTEGER',
                    'PositiveSmallIntegerField': 'INTEGER',
                    'UUIDField': 'CHAR(36)',
                }
            else:
                # Default fallback
                type_mapping = {
                    'AutoField': 'INTEGER',
                    'BigAutoField': 'BIGINT',
                    'IntegerField': 'INTEGER',
                    'BigIntegerField': 'BIGINT',
                    'SmallIntegerField': 'SMALLINT',
                    'UUIDField': 'CHAR(36)',
                }
            
            # Return the appropriate type or default to INTEGER
            fk_type = type_mapping.get(pk_field_type, 'INTEGER')
            
            if debug_mode:
                print(f"✅ FieldMapper._get_foreign_key_type: Mapped '{pk_field_type}' to '{fk_type}'")
            
            return fk_type
            
        except Exception as e:
            error_msg = f"Error determining foreign key type: {e}"
            if debug_mode:
                print(f"❌ FieldMapper._get_foreign_key_type: {error_msg}")
            
            # Fallback to default type if we can't determine the referenced type
            if self.engine == 'mysql':
                return 'INT'
            else:
                return 'INTEGER'
    
    def _get_json_field_type(self, field):
        """
        Get the correct JSON field type based on database engine and field configuration
        
        This method returns the appropriate JSON type for different database engines:
        - MySQL: JSON type
        - PostgreSQL: JSONB type
        - SQLite: TEXT type (no native JSON support)
        
        Args:
            field: Django JSONField instance
            
        Returns:
            str: Database column type for JSON field
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 FieldMapper._get_json_field_type: Getting JSON type for field '{field.name}'")
        
        try:
            # Handle default value for JSON fields
            default_value = getattr(field, 'default', None)
            
            if debug_mode:
                print(f"   Default value: {default_value}")
            
            if self.engine == 'mysql':
                # MySQL JSON field - always return JSON type, handle defaults separately
                json_type = 'JSON'
            elif self.engine == 'postgresql':
                json_type = 'JSONB'
            elif self.engine == 'sqlite':
                json_type = 'TEXT'  # SQLite doesn't have native JSON, use TEXT
            else:
                json_type = 'JSON'
            
            if debug_mode:
                print(f"✅ FieldMapper._get_json_field_type: Using '{json_type}' for '{self.engine}' engine")
            
            return json_type
                
        except Exception as e:
            error_msg = f"Error determining JSON field type: {e}"
            if debug_mode:
                print(f"❌ FieldMapper._get_json_field_type: {error_msg}")
            
            # Fallback to safe default
            if self.engine == 'mysql':
                return 'JSON'
            elif self.engine == 'postgresql':
                return 'JSONB'
            else:
                return 'TEXT'

    def field_to_column_definition(self, field):
        """
        Convert Django field to database column definition
        
        This is the main method that converts a Django model field to a complete
        database column definition including:
        - Base type (VARCHAR, INT, etc.)
        - Nullability constraints (NOT NULL)
        - Default values
        - Primary key constraints
        - Unique constraints
        
        Args:
            field: Django model field instance
            
        Returns:
            str: Complete SQL column definition
            None: For ManyToManyField (handled separately)
            
        Raises:
            FieldMappingError: If field type is not supported
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 FieldMapper.field_to_column_definition: Converting field '{field.name}' to column definition")
        
        field_type = type(field).__name__
        
        if debug_mode:
            print(f"   Field type: {field_type}")
            print(f"   Nullable: {getattr(field, 'null', False)}")
            print(f"   Primary key: {getattr(field, 'primary_key', False)}")
            print(f"   Unique: {getattr(field, 'unique', False)}")
        
        # Skip ManyToManyField - these are handled separately via intermediate tables
        if field_type == 'ManyToManyField':
            if debug_mode:
                print(f"   Skipping ManyToManyField - handled separately")
            return None  # Signal that this field should be handled separately
        
        # Get base type
        mapper = self.type_mappings.get(field_type)
        if not mapper:
            error_msg = f"Unsupported field type: {field_type}"
            if debug_mode:
                print(f"❌ FieldMapper.field_to_column_definition: {error_msg}")
            raise FieldMappingError(error_msg)
        
        base_type = mapper(field)
        
        if debug_mode:
            print(f"   Base type: {base_type}")
        
        # Add constraints
        constraints = []
        
        # Only add NOT NULL for non-nullable fields
        is_nullable = getattr(field, 'null', False)
        if not is_nullable:
            constraints.append('NOT NULL')
            if debug_mode:
                print(f"   Added constraint: NOT NULL")
        # Do NOT add 'NULL' for nullable fields
        
        # Default value handling
        if hasattr(field, 'default') and field.default != models.NOT_PROVIDED:
            default_value = field.default
            
            if debug_mode:
                print(f"   Processing default value: {default_value} (type: {type(default_value).__name__})")
            
            if default_value is None:
                constraints.append('DEFAULT NULL')
                if debug_mode:
                    print(f"   Added constraint: DEFAULT NULL")
            elif isinstance(default_value, str):
                constraints.append(f"DEFAULT '{default_value}'")
                if debug_mode:
                    print(f"   Added constraint: DEFAULT '{default_value}'")
            elif isinstance(default_value, bool):
                default_val = 'TRUE' if default_value else 'FALSE'
                if self.engine == 'mysql':
                    default_val = '1' if default_value else '0'
                constraints.append(f'DEFAULT {default_val}')
                if debug_mode:
                    print(f"   Added constraint: DEFAULT {default_val}")
            elif callable(default_value):
                # Handle callable defaults (like timezone.now, uuid.uuid4, etc.)
                if hasattr(default_value, '__name__'):
                    if default_value.__name__ == 'now':
                        constraints.append('DEFAULT CURRENT_TIMESTAMP')
                        if debug_mode:
                            print(f"   Added constraint: DEFAULT CURRENT_TIMESTAMP")
                    elif default_value.__name__ == 'uuid4':
                        constraints.append('DEFAULT UUID()')
                        if debug_mode:
                            print(f"   Added constraint: DEFAULT UUID()")
                    elif default_value.__name__ == 'today':
                        constraints.append('DEFAULT CURRENT_DATE')
                        if debug_mode:
                            print(f"   Added constraint: DEFAULT CURRENT_DATE")
                    elif default_value.__name__ == 'time':
                        constraints.append('DEFAULT CURRENT_TIME')
                        if debug_mode:
                            print(f"   Added constraint: DEFAULT CURRENT_TIME")
                    else:
                        # For other callables, try to get a sample value
                        try:
                            sample_value = default_value()
                            if isinstance(sample_value, str):
                                constraints.append(f"DEFAULT '{sample_value}'")
                                if debug_mode:
                                    print(f"   Added constraint: DEFAULT '{sample_value}'")
                            else:
                                constraints.append(f'DEFAULT {sample_value}')
                                if debug_mode:
                                    print(f'Added constraint: DEFAULT {sample_value}')
                        except:
                            if debug_mode:
                                print(f"   Skipping callable default: {default_value}")
                            pass
                else:
                    if debug_mode:
                        print(f"   Skipping callable default: {default_value}")
                    pass        
           
           
           
            elif field_type == 'JSONField':
                if callable(default_value):
                    if debug_mode:
                        print(f"   Skipping callable default for JSONField")
                    pass
                else:
                    constraints.append(f"DEFAULT '{default_value}'")
                    if debug_mode:
                        print(f"   Added constraint: DEFAULT '{default_value}'")
            else:
                constraints.append(f'DEFAULT {default_value}')
                if debug_mode:
                    print(f"   Added constraint: DEFAULT {default_value}")
        else:
            if debug_mode:
                print(f"   No default value specified")
        # DO NOT add DEFAULT NULL for nullable fields without an explicit default!
        # (No else/elif here)
        
        # Primary key (for non-auto fields)
        if getattr(field, 'primary_key', False) and 'AUTO' not in base_type.upper():
            constraints.append('PRIMARY KEY')
            if debug_mode:
                print(f"   Added constraint: PRIMARY KEY")
        
        # Unique constraint
        if getattr(field, 'unique', False):
            constraints.append('UNIQUE')
            if debug_mode:
                print(f"   Added constraint: UNIQUE")
        
        # Build final column definition
        column_definition = f"{base_type} {' '.join(constraints)}".strip()
        
        if debug_mode:
            print(f"✅ FieldMapper.field_to_column_definition: Final definition: {column_definition}")
        
        return column_definition