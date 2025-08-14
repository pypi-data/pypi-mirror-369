import logging
from django.db import connections
from django.apps import apps
from .exceptions import DatabaseConnectionError
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

class DatabaseInspector:
    """
    Inspect database structure and compare with Django models
    
    This class provides methods to:
    - Connect to the database
    - Get table and column information
    - Retrieve constraints and indexes
    - Compare database schema with Django models
    """
    
    def __init__(self, database_alias='default'):
        """
        Initialize DatabaseInspector with database connection
        
        Args:
            database_alias (str): Django database alias to connect to
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 DatabaseInspector.__init__: Initializing with database_alias='{database_alias}'")
        
        self.database_alias = database_alias
        self.connection = None
        self.cursor = None
        self._connect()
        
        if debug_mode:
            print(f"✅ DatabaseInspector.__init__: Successfully initialized for database '{database_alias}'")
    
    def _connect(self):
        """
        Establish database connection using Django's connection framework
        
        This method:
        1. Gets the database connection from Django's connection manager
        2. Creates a cursor for executing queries
        3. Handles connection errors gracefully
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 DatabaseInspector._connect: Attempting to connect to database '{self.database_alias}'")
        
        try:
            self.connection = connections[self.database_alias]
            self.cursor = self.connection.cursor()
            
            if debug_mode:
                print(f"✅ DatabaseInspector._connect: Successfully connected to database '{self.database_alias}'")
                print(f"   Engine: {self.connection.vendor}")
                print(f"   Database: {self.connection.settings_dict.get('NAME', 'Unknown')}")
            
            log_info(f"Connected to database: {self.database_alias}")
        except Exception as e:
            error_msg = f"Failed to connect to {self.database_alias}: {e}"
            if debug_mode:
                print(f"❌ DatabaseInspector._connect: {error_msg}")
            raise DatabaseConnectionError(error_msg)
    
    def get_database_engine(self):
        """
        Get the database engine type (mysql, postgresql, sqlite, etc.)
        
        Returns:
            str: Database vendor/engine name
        """
        debug_mode = get_setting('DEBUG_MODE')
        engine = self.connection.vendor
        
        if debug_mode:
            print(f"🔍 DatabaseInspector.get_database_engine: Returning engine '{engine}'")
        
        return engine
    
    def get_existing_tables(self):
        """
        Get list of existing tables in the database
        
        This method uses Django's introspection to get all table names.
        It's used to determine which tables already exist before creating new ones.
        
        Returns:
            list: List of table names in the database
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 DatabaseInspector.get_existing_tables: Getting all table names from database")
        
        tables = self.connection.introspection.table_names()
        
        if debug_mode:
            print(f"✅ DatabaseInspector.get_existing_tables: Found {len(tables)} tables")
            if len(tables) <= 10:  # Only show all tables if there are 10 or fewer
                print(f"   Tables: {', '.join(tables)}")
            else:
                print(f"   Tables: {', '.join(tables[:5])}... and {len(tables)-5} more")
        
        return tables
    
    def get_table_description(self, table_name):
        """
        Get detailed column information for a specific table
        
        This method returns information about each column including:
        - Column name
        - Data type
        - Nullability
        - Size/precision
        - Scale
        
        Args:
            table_name (str): Name of the table to inspect
            
        Returns:
            list: List of column description objects
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 DatabaseInspector.get_table_description: Getting column info for table '{table_name}'")
        
        description = self.connection.introspection.get_table_description(self.cursor, table_name)
        
        if debug_mode:
            print(f"✅ DatabaseInspector.get_table_description: Found {len(description)} columns in '{table_name}'")
            for col in description:
                print(f"   Column: {col.name} ({col.type_code}) - Nullable: {col.null_ok}")
        
        return description
    
    def get_table_constraints(self, table_name):
        """
        Get all constraints for a specific table
        
        This method returns information about:
        - Primary keys
        - Foreign keys
        - Unique constraints
        - Check constraints
        
        Args:
            table_name (str): Name of the table to inspect
            
        Returns:
            dict: Dictionary of constraint information
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 DatabaseInspector.get_table_constraints: Getting constraints for table '{table_name}'")
        
        constraints = self.connection.introspection.get_constraints(self.cursor, table_name)
        
        if debug_mode:
            print(f"✅ DatabaseInspector.get_table_constraints: Found {len(constraints)} constraints in '{table_name}'")
            for constraint_name, constraint_info in constraints.items():
                constraint_type = []
                if constraint_info.get('primary_key'):
                    constraint_type.append('PRIMARY KEY')
                if constraint_info.get('unique'):
                    constraint_type.append('UNIQUE')
                if constraint_info.get('foreign_key'):
                    constraint_type.append('FOREIGN KEY')
                if constraint_info.get('check'):
                    constraint_type.append('CHECK')
                print(f"   Constraint: {constraint_name} ({', '.join(constraint_type)})")
        
        return constraints
    
    def get_foreign_key_constraints(self, table_name):
        """
        Get foreign key constraints for a specific table
        
        This method filters the general constraints to return only foreign key constraints.
        It's used to understand relationships between tables.
        
        Args:
            table_name (str): Name of the table to inspect
            
        Returns:
            dict: Dictionary of foreign key constraint information
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 DatabaseInspector.get_foreign_key_constraints: Getting FK constraints for table '{table_name}'")
        
        try:
            all_constraints = self.get_table_constraints(table_name)
            foreign_key_constraints = {}
            
            for constraint_name, constraint_info in all_constraints.items():
                # Check if this is a foreign key constraint
                if constraint_info.get('foreign_key'):
                    foreign_key_constraints[constraint_name] = {
                        'constrained_columns': constraint_info.get('columns', []),
                        'referred_table': constraint_info.get('foreign_key')[0] if constraint_info.get('foreign_key') else None,
                        'referred_columns': constraint_info.get('foreign_key')[1] if constraint_info.get('foreign_key') and len(constraint_info.get('foreign_key', [])) > 1 else []
                    }
            
            if debug_mode:
                print(f"✅ DatabaseInspector.get_foreign_key_constraints: Found {len(foreign_key_constraints)} FK constraints in '{table_name}'")
                for fk_name, fk_info in foreign_key_constraints.items():
                    print(f"   FK: {fk_name} -> {fk_info['referred_table']}.{fk_info['referred_columns']}")
            
            return foreign_key_constraints
            
        except Exception as e:
            error_msg = f"Could not get foreign key constraints for {table_name}: {e}"
            if debug_mode:
                print(f"❌ DatabaseInspector.get_foreign_key_constraints: {error_msg}")
            log_warning(error_msg)
            return {}
    
    def get_table_indexes(self, table_name):
        """
        Get indexes for a specific table
        
        This method returns information about database indexes including:
        - Index names
        - Indexed columns
        - Index types (unique, etc.)
        
        Args:
            table_name (str): Name of the table to inspect
            
        Returns:
            dict: Dictionary of index information
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 DatabaseInspector.get_table_indexes: Getting indexes for table '{table_name}'")
        
        indexes = self.connection.introspection.get_indexes(self.cursor, table_name)
        
        if debug_mode:
            print(f"✅ DatabaseInspector.get_table_indexes: Found {len(indexes)} indexes in '{table_name}'")
            for index_name, index_info in indexes.items():
                unique = "UNIQUE" if index_info.get('unique') else "NON-UNIQUE"
                print(f"   Index: {index_name} ({unique}) on columns: {index_info.get('columns', [])}")
        
        return indexes
    
    def get_database_info(self):
        """
        Get comprehensive database information
        
        This method provides a complete overview of the database structure including:
        - Database engine
        - All tables and their columns
        - Constraints for each table
        - Total table count
        
        This is useful for debugging and understanding the current database state.
        
        Returns:
            dict: Comprehensive database information dictionary
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 DatabaseInspector.get_database_info: Getting comprehensive database information")
        
        tables = self.get_existing_tables()
        db_info = {
            'engine': self.get_database_engine(),
            'tables': {},
            'total_tables': len(tables)
        }
        
        if debug_mode:
            print(f"   Database engine: {db_info['engine']}")
            print(f"   Total tables: {db_info['total_tables']}")
        
        for table in tables:
            try:
                if debug_mode:
                    print(f"   Inspecting table: {table}")
                
                description = self.get_table_description(table)
                constraints = self.get_table_constraints(table)
                
                db_info['tables'][table] = {
                    'columns': {col.name: {
                        'type': col.type_code,
                        'display_size': col.display_size,
                        'internal_size': col.internal_size,
                        'precision': col.precision,
                        'scale': col.scale,
                        'null_ok': col.null_ok,
                    } for col in description},
                    'constraints': constraints,
                }
                
                if debug_mode:
                    print(f"   ✅ Successfully inspected table '{table}' ({len(description)} columns, {len(constraints)} constraints)")
                    
            except Exception as e:
                error_msg = f"Could not inspect table {table}: {e}"
                if debug_mode:
                    print(f"   ❌ {error_msg}")
                log_warning(error_msg)
                db_info['tables'][table] = {'error': str(e)}
        
        if debug_mode:
            print(f"✅ DatabaseInspector.get_database_info: Completed database inspection")
        
        return db_info
    
    def close(self):
        """
        Close database connection and cleanup resources
        
        This method properly closes the cursor and cleans up the connection.
        Note: Django connections are managed automatically, so we only need to close the cursor.
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 DatabaseInspector.close: Closing database connection")
        
        if self.cursor:
            self.cursor.close()
            if debug_mode:
                print(f"✅ DatabaseInspector.close: Cursor closed successfully")
        
        # Django connections are managed automatically
        if debug_mode:
            print(f"✅ DatabaseInspector.close: Connection cleanup completed")