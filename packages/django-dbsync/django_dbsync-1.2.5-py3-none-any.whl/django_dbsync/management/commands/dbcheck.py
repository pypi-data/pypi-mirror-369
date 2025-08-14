from django.core.management.base import BaseCommand
from django.db import connections
from colorama import init, Fore, Style
from tabulate import tabulate

from ...core.database_inspector import DatabaseInspector
from ...utils.helpers import report_table_case_mismatches, report_table_name_conflicts

init(autoreset=True)

class Command(BaseCommand):
    help = 'Check database schema and show detailed information'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--database',
            type=str,
            default='default',
            help='Database alias to check (default: default)'
        )
        
        parser.add_argument(
            '--table',
            type=str,
            help='Show details for specific table'
        )
        
        parser.add_argument(
            '--compare-models',
            action='store_true',
            help='Compare database with Django models'
        )
        
        parser.add_argument(
            '--check-case-mismatches',
            action='store_true',
            help='Check for table name case mismatches between models and database'
        )
        
        parser.add_argument(
            '--check-name-conflicts',
            action='store_true',
            help='Check for table name conflicts (both lowercase and uppercase versions exist)'
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write(f"{Fore.CYAN}Database Schema Check{Style.RESET_ALL}")
        self.stdout.write("=" * 40)
        
        try:
            if options['check_case_mismatches']:
                self._check_case_mismatches(options['database'])
            elif options['check_name_conflicts']:
                self._check_name_conflicts(options['database'])
            else:
                inspector = DatabaseInspector(options['database'])
                
                if options['table']:
                    self._show_table_details(inspector, options['table'])
                elif options['compare_models']:
                    self._compare_with_models(inspector)
                else:
                    self._show_database_overview(inspector)
                
        except Exception as e:
            self.stdout.write(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    def _show_database_overview(self, inspector):
        """Show database overview"""
        db_info = inspector.get_database_info()
        
        self.stdout.write(f"Database Engine: {Fore.BLUE}{db_info['engine']}{Style.RESET_ALL}")
        self.stdout.write(f"Total Tables: {Fore.GREEN}{db_info['total_tables']}{Style.RESET_ALL}")
        self.stdout.write()
        
        # Table list
        table_data = []
        for table_name, table_info in db_info['tables'].items():
            if 'error' in table_info:
                table_data.append([table_name, "ERROR", "ERROR", table_info['error']])
            else:
                column_count = len(table_info.get('columns', {}))
                constraint_count = len(table_info.get('constraints', {}))
                table_data.append([table_name, column_count, constraint_count, "OK"])
        
        headers = ["Table Name", "Columns", "Constraints", "Status"]
        self.stdout.write(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def _show_table_details(self, inspector, table_name):
        """Show detailed information for a specific table"""
        try:
            existing_tables = inspector.get_existing_tables()
            if table_name not in existing_tables:
                self.stdout.write(f"{Fore.RED}Table '{table_name}' not found in database{Style.RESET_ALL}")
                return
                
            self.stdout.write(f"\n{Fore.CYAN}Table Details: {table_name}{Style.RESET_ALL}")
            self.stdout.write("-" * 50)
            
            # Get table description
            description = inspector.get_table_description(table_name)
            
            # Column information
            column_data = []
            for col in description:
                # Django introspection returns column objects with these attributes:
                # name, type_code, display_size, internal_size, precision, scale, null_ok
                column_data.append([
                    col.name,
                    col.type_code or 'UNKNOWN',
                    'YES' if col.null_ok else 'NO',
                    '',  # Default value not available from introspection
                    ''   # Key type not available from basic introspection
                ])
            
            headers = ["Column", "Type", "Null", "Default", "Key"]
            self.stdout.write(tabulate(column_data, headers=headers, tablefmt="grid"))
            
            # Foreign key constraints
            constraints = inspector.get_foreign_key_constraints(table_name)
            if constraints:
                self.stdout.write(f"\n{Fore.YELLOW}Foreign Key Constraints:{Style.RESET_ALL}")
                constraint_data = []
                for constraint_name, constraint_info in constraints.items():
                    constraint_data.append([
                        constraint_name,
                        ', '.join(constraint_info['constrained_columns']),
                        constraint_info['referred_table'],
                        ', '.join(constraint_info['referred_columns'])
                    ])
                
                headers = ["Constraint", "Column(s)", "Referenced Table", "Referenced Column(s)"]
                self.stdout.write(tabulate(constraint_data, headers=headers, tablefmt="grid"))
            
            # Table statistics
            try:
                inspector.cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                row_count = inspector.cursor.fetchone()[0]
                self.stdout.write(f"\n{Fore.GREEN}Row Count: {row_count}{Style.RESET_ALL}")
            except Exception as e:
                self.stdout.write(f"\n{Fore.RED}Could not get row count: {e}{Style.RESET_ALL}")
                
        except Exception as e:
            self.stdout.write(f"{Fore.RED}Error showing table details: {e}{Style.RESET_ALL}")
    
    def _compare_with_models(self, inspector):
        """Compare database schema with Django models"""
        try:
            from django.apps import apps
            from ...core.sync_engine import SyncEngine
            
            self.stdout.write(f"\n{Fore.CYAN}Database vs Django Models Comparison{Style.RESET_ALL}")
            self.stdout.write("-" * 50)
            
            sync_engine = SyncEngine(inspector.database_alias)
            models_list = sync_engine.get_models_to_sync()
            existing_tables = inspector.get_existing_tables()
            
            comparison_data = []
            
            # Check each model
            for model in models_list:
                table_name = sync_engine.get_table_name(model)
                
                if table_name in existing_tables:
                    # Table exists - check columns
                    existing_columns = sync_engine._get_existing_columns(table_name)
                    model_columns = sync_engine.get_model_columns(model)
                    
                    missing_columns = set(model_columns.keys()) - set(existing_columns.keys())
                    extra_columns = set(existing_columns.keys()) - set(model_columns.keys())
                    
                    if missing_columns or extra_columns:
                        status = f"{Fore.YELLOW}MISMATCH{Style.RESET_ALL}"
                        issues = []
                        if missing_columns:
                            issues.append(f"Missing: {', '.join(missing_columns)}")
                        if extra_columns:
                            issues.append(f"Extra: {', '.join(extra_columns)}")
                        details = "; ".join(issues)
                    else:
                        status = f"{Fore.GREEN}OK{Style.RESET_ALL}"
                        details = "Columns match"
                else:
                    status = f"{Fore.RED}MISSING{Style.RESET_ALL}"
                    details = "Table does not exist in database"
                
                comparison_data.append([
                    f"{model._meta.app_label}.{model.__name__}",
                    table_name,
                    status,
                    details
                ])
            
            # Check for orphaned tables
            model_tables = {sync_engine.get_table_name(model) for model in models_list}
            orphaned_tables = set(existing_tables) - model_tables
            
            # Filter out system tables
            field_mapper = sync_engine.field_mapper
            orphaned_tables = {table for table in orphaned_tables 
                             if not field_mapper.should_exclude_table(table)}
            
            for table in orphaned_tables:
                comparison_data.append([
                    "(No Model)",
                    table,
                    f"{Fore.YELLOW}ORPHANED{Style.RESET_ALL}",
                    "Table exists but no corresponding Django model"
                ])
            
            headers = ["Django Model", "Database Table", "Status", "Details"]
            self.stdout.write(tabulate(comparison_data, headers=headers, tablefmt="grid"))
            
        except Exception as e:
            self.stdout.write(f"{Fore.RED}Error comparing with models: {e}{Style.RESET_ALL}")
    
    def _check_case_mismatches(self, database_alias):
        """Check for table name case mismatches"""
        self.stdout.write(f"{Fore.YELLOW}Checking for table name case mismatches...{Style.RESET_ALL}")
        self.stdout.write()
        
        report_table_case_mismatches(database_alias)
    
    def _check_name_conflicts(self, database_alias):
        """Check for table name conflicts"""
        self.stdout.write(f"{Fore.YELLOW}Checking for table name conflicts...{Style.RESET_ALL}")
        self.stdout.write()
        
        report_table_name_conflicts(database_alias)