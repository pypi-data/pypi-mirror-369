from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from colorama import init, Fore, Style
import os
import sys
import json
import time
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

from ...core.sync_engine import SyncEngine
from ...core.database_inspector import DatabaseInspector
from ...core.exceptions import SyncOperationError
from ...settings import get_setting
from ...utils.helpers import generate_orphaned_models_report, list_database_views, generate_views_report

init(autoreset=True)  # Initialize colorama

class TeeOutput:
    """
    Custom output handler that writes to both console and file
    """
    def __init__(self, original_stdout, log_file):
        self.original_stdout = original_stdout
        self.log_file = log_file
        
    def write(self, text):
        # Write to original stdout (console)
        self.original_stdout.write(text)
        # Write to log file
        if self.log_file:
            self.log_file.write(text)
            self.log_file.flush()  # Ensure immediate writing
            
    def flush(self):
        self.original_stdout.flush()
        if self.log_file:
            self.log_file.flush()
            
    def isatty(self):
        # Preserve tty behavior for colorama
        return self.original_stdout.isatty()

class Command(BaseCommand):
    """
    Django management command for synchronizing Django models with database schema
    
    This command provides comprehensive database synchronization capabilities including:
    - Model-to-database schema synchronization
    - Table creation, modification, and deletion
    - Foreign key constraint management
    - Many-to-many relationship handling
    - Backup creation and restoration
    - Detailed reporting and logging
    - Orphaned table management
    - Database views management
    """
    
    help = 'Synchronize Django models with database schema'
    
    def add_arguments(self, parser):
        """
        Define command line arguments for the dbsync command
        
        This method sets up all available command line options including:
        - Database selection
        - Dry run mode
        - Auto approval settings
        - App and table filtering
        - Backup and reporting options
        - Safety and manual command options
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 Command.add_arguments: Setting up command line arguments")
        
        parser.add_argument(
            '--database', '-d',
            type=str,
            default='default',
            help='Database alias to use (default: default)'
        )
        
        parser.add_argument(
            '--dry-run', '-dr',
            action='store_true',
            help='Show what would be done without making changes'
        )
        
        parser.add_argument(
            '--auto-approve', '-aa',
            action='store_true',
            help='Automatically approve all operations without prompting'
        )
        
        parser.add_argument(
            '--exclude-apps', '-ea',
            nargs='*',
            help='Apps to exclude from synchronization'
        )
        
        parser.add_argument(
            '--include-apps', '-ia',
            nargs='*',
            help='Apps to include in synchronization (only these will be synced)'
        )
        
        parser.add_argument(
            '--backup', '-b',
            action='store_true',
            help='Create backup before synchronization'
        )
        
        parser.add_argument(
            '--report', '-r',
            choices=['json', 'html', 'both'],
            help='Generate report after synchronization'
        )
        
        parser.add_argument(
            '--show-orphaned', '-so',
            action='store_true',
            help='Show orphaned tables after synchronization'
        )
        
        parser.add_argument(
            '--drop-orphaned', '-do',
            action='store_true',
            help='Drop orphaned tables (use with caution!)'
        )
        
        parser.add_argument(
            '--exclude-table-patterns', '-etp',
            nargs='*',
            help='Regex patterns for tables to exclude'
        )
        
        parser.add_argument(
            '--no-restriction', '-nr',
            action='store_true',
            help='Disable all restrictions and include all models/tables'
        )
        
        parser.add_argument(
            '--exclude-app-patterns', '-eap',
            nargs='*',
            help='Regex patterns for apps to exclude'
        )
        
        parser.add_argument(
            '--suggest-manual-commands', '-smc',
            action='store_true',
            help='Show manual SQL commands for table renames (automatically shown in dry-run mode)'
        )
        
        parser.add_argument(
            '--generate-orphaned-models', '-gom',
            action='store_true',
            help='Generate Django models for orphaned tables'
        )
        
        parser.add_argument(
            '--report-views', '-rv',
            action='store_true',
            help='Generate a report and Django models for all database views'
        )
        
        parser.add_argument(
            '--list-views', '-lv',
            action='store_true',
            help='List all database views'
        )
        
        parser.add_argument(
            '--txt-log', '-tl',
            type=str,
            help='Save terminal output to a text file'
        )
        
        parser.add_argument(
            '--retry-failed', '-rf',
            action='store_true',
            help='Retry failed operations (foreign keys, M2M tables) up to 3 times'
        )
        
        parser.add_argument(
            '--max-retries', '-mr',
            type=int,
            default=3,
            help='Maximum number of retry attempts for failed operations (default: 3)'
        )
        
        if debug_mode:
            print(f"✅ Command.add_arguments: Added {len(parser._option_string_actions)} command line arguments")
    
    def handle(self, *args, **options):
        """
        Main command handler for the dbsync command
        
        This method orchestrates the entire synchronization process:
        1. Validates command line options
        2. Initializes the sync engine
        3. Handles special operations (views, orphaned tables)
        4. Performs database synchronization
        5. Generates reports and displays results
        6. Handles errors and provides user feedback
        
        Args:
            *args: Variable length argument list
            **options: Command line options dictionary
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 Command.handle: Starting dbsync command execution")
            print(f"   Options: {options}")
        
        version = get_setting('VERSION', '1.0.0')
        
        # Handle txt-log option
        log_file = None
        original_stdout = sys.stdout
        if options['txt_log']:
            try:
                # Use the same output directory as other reports
                output_dir = get_setting('REPORT_OUTPUT_DIR', 'dbsync_reports/')
                os.makedirs(output_dir, exist_ok=True)
                
                # Create filename with timestamp if just filename provided, or use full path
                if os.path.dirname(options['txt_log']) == '':
                    # Just filename provided, use it directly in reports directory
                    log_file_path = os.path.join(output_dir, options['txt_log'])
                else:
                    # Full path provided, use as is
                    log_file_path = options['txt_log']
                
                log_file = open(log_file_path, 'w', encoding='utf-8')
                sys.stdout = TeeOutput(original_stdout, log_file)
                if debug_mode:
                    print(f"🔍 Command.handle: Text logging enabled - output will be saved to {log_file_path}")
            except Exception as e:
                error_msg = f"Error opening log file '{log_file_path}': {e}"
                if debug_mode:
                    print(f"❌ Command.handle: {error_msg}")
                self.stdout.write(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
                return
        
        self.stdout.write(
            f"{Fore.CYAN}Django Database Sync v{version}{Style.RESET_ALL}"
        )
        self.stdout.write("=" * 50)
        
        try:
            if debug_mode:
                print(f"🔍 Command.handle: Processing command options")
            
            # Handle views operations first (these don't require sync)
            if options['list_views']:
                if debug_mode:
                    print(f"🔍 Command.handle: Processing --list-views option")
                from ...utils.helpers import list_database_views
                try:
                    view_count, view_names = list_database_views(options['database'], names_only=True)
                    self.stdout.write(f"\n{Fore.CYAN}Database Views:{Style.RESET_ALL}")
                    self.stdout.write(f"Total Views: {view_count}")
                    if view_names:
                        for name in view_names:
                            self.stdout.write(f"- {name}")
                    else:
                        self.stdout.write("No views found.")
                    if debug_mode:
                        print(f"✅ Command.handle: Successfully listed {view_count} views")
                except Exception as e:
                    error_msg = f"Error listing views: {e}"
                    if debug_mode:
                        print(f"❌ Command.handle: {error_msg}")
                    self.stdout.write(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            
            if options['report_views']:
                if debug_mode:
                    print(f"🔍 Command.handle: Processing --report-views option")
                from ...utils.helpers import generate_views_report
                try:
                    filepath, views = generate_views_report(options['database'])
                    if views:
                        self.stdout.write(f"{Fore.GREEN}✅ Views report generated: {filepath}{Style.RESET_ALL}")
                        self.stdout.write(f"{Fore.CYAN}Database Views:{Style.RESET_ALL}")
                        for view in views:
                            self.stdout.write(f"  - {view['name']} (columns: {', '.join(view['columns'])})")
                        if debug_mode:
                            print(f"✅ Command.handle: Successfully generated views report with {len(views)} views")
                    else:
                        self.stdout.write(f"{Fore.YELLOW}ℹ️  No views found in the database{Style.RESET_ALL}")
                        if debug_mode:
                            print(f"ℹ️ Command.handle: No views found in database")
                except Exception as e:
                    error_msg = f"Error generating views report: {e}"
                    if debug_mode:
                        print(f"❌ Command.handle: {error_msg}")
                    self.stdout.write(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            
            # If only views operations are requested, skip all sync/orphaned logic
            sync_flags = [
                options['exclude_apps'],
                options['exclude_table_patterns'], options['exclude_app_patterns'],
                options['no_restriction'], options['drop_orphaned']
            ]
            if (options['list_views'] or options['report_views']) and not any(sync_flags):
                if debug_mode:
                    print(f"✅ Command.handle: Views-only operation completed, skipping sync logic")
                self.stdout.write(f"{Fore.GREEN}Views operation completed!{Style.RESET_ALL}")
                return
            
            if debug_mode:
                print(f"🔍 Command.handle: Initializing sync engine")
            
            # Initialize sync engine
            sync_engine = SyncEngine(
                database_alias=options['database'],
                dry_run=options['dry_run'],
                auto_approve=options['auto_approve']
            )
            
            # Configure retry settings
            if options['retry_failed']:
                sync_engine.set_retry_failed(True)
                sync_engine.set_max_retries(options['max_retries'])
                if debug_mode:
                    print(f"   Retry mechanism enabled with max {options['max_retries']} attempts")
                self.stdout.write(f"{Fore.CYAN}🔄 Retry mechanism enabled - will retry failed operations up to {options['max_retries']} times{Style.RESET_ALL}")
            
            if debug_mode:
                print(f"✅ Command.handle: Sync engine initialized successfully")
                print(f"🔍 Command.handle: Configuring sync engine options")
            
            # Configure options
            if options['exclude_apps']:
                if debug_mode:
                    print(f"   Setting excluded apps: {options['exclude_apps']}")
                sync_engine.set_excluded_apps(options['exclude_apps'])
            
            if options['include_apps']:
                if debug_mode:
                    print(f"   Setting included apps: {options['include_apps']}")
                sync_engine.set_included_apps(options['include_apps'])
            
            # Apply regex patterns from command line
            if options['exclude_table_patterns']:
                if debug_mode:
                    print(f"   Setting exclude table patterns: {options['exclude_table_patterns']}")
                sync_engine.set_exclude_table_patterns(options['exclude_table_patterns'])
            
            if options['exclude_app_patterns']:
                if debug_mode:
                    print(f"   Setting exclude app patterns: {options['exclude_app_patterns']}")
                sync_engine.set_exclude_app_patterns(options['exclude_app_patterns'])
            
            # Handle no-restriction flag
            if options['no_restriction']:
                if debug_mode:
                    print(f"   Enabling no-restriction mode")
                sync_engine.set_no_restriction(True)
                self.stdout.write(f"{Fore.YELLOW}⚠️  No-restriction mode enabled: ALL Django tables will be synced (including auth, admin, sessions, etc.){Style.RESET_ALL}")
            
            # Create backup if requested
            if options['backup']:
                if debug_mode:
                    print(f"🔍 Command.handle: Creating backup before sync")
                self.stdout.write(f"{Fore.YELLOW}Creating backup...{Style.RESET_ALL}")
                backup_file = sync_engine.create_backup()
                self.stdout.write(f"{Fore.GREEN}Backup created: {backup_file}{Style.RESET_ALL}")
                if debug_mode:
                    print(f"✅ Command.handle: Backup created successfully: {backup_file}")

            # Initialize results variable
            results = {}
            
            # Handle orphaned tables if requested
            if options['drop_orphaned'] and not any([
                options['exclude_apps'], options['include_apps'],
                options['exclude_table_patterns'], options['exclude_app_patterns'],
                options['no_restriction']
            ]):
                if debug_mode:
                    print(f"🔍 Command.handle: Processing orphaned tables only")
                orphaned_tables = sync_engine.get_orphaned_tables()
                self._handle_orphaned_tables(sync_engine, orphaned_tables, options['dry_run'])
            else:
                # Run full synchronization
                if debug_mode:
                    print(f"🔍 Command.handle: Starting full model synchronization")
                self.stdout.write(f"{Fore.BLUE}Starting synchronization...{Style.RESET_ALL}")
                results = sync_engine.sync_all_models()
                
                # Reset dry run mode after sync to ensure subsequent operations are not in dry run
                if options['dry_run']:
                    if debug_mode:
                        print(f"🔍 Command.handle: Resetting dry run mode after sync")
                    sync_engine.reset_dry_run()
                    self.stdout.write(f"{Fore.YELLOW}⚠️  Dry run mode reset after sync{Style.RESET_ALL}")
                
            # Show results only if we have results to show
            if results:
                if debug_mode:
                    print(f"🔍 Command.handle: Displaying sync results")
                self._display_results(results)
            
            # Show retry results if retry mechanism was used
            if options['retry_failed'] and hasattr(sync_engine, 'still_failed_after_retry'):
                self._display_retry_results(sync_engine.still_failed_after_retry)
            
            # Display manual commands only if --suggest-manual-commands is used
            if options['suggest_manual_commands']:
                if debug_mode:
                    print(f"🔍 Command.handle: Displaying manual commands")
                sync_engine.display_manual_commands()
            
            # Show orphaned tables if requested (but not if we already handled them above)
            if (options['show_orphaned'] or get_setting('SHOW_ORPHANED_TABLES')) and not options['drop_orphaned']:
                if debug_mode:
                    print(f"🔍 Command.handle: Getting and displaying orphaned tables")
                orphaned = sync_engine.get_orphaned_tables()
                self._display_orphaned_tables(orphaned)
            
            # Generate report if requested and we have results
            if options['report'] and results:
                if debug_mode:
                    print(f"🔍 Command.handle: Generating {options['report']} report")
                self._generate_report(results, options['report'])
            
            # Generate orphaned models report if requested
            if options['generate_orphaned_models']:
                if debug_mode:
                    print(f"🔍 Command.handle: Generating orphaned models report")
                orphaned_tables = sync_engine.get_orphaned_tables()
                if orphaned_tables:
                    output_dir = get_setting('REPORT_OUTPUT_DIR', 'dbsync_reports/')
                    filepath = generate_orphaned_models_report(
                        orphaned_tables, 
                        options['database'], 
                        output_dir
                    )
                    if filepath:
                        self.stdout.write(f"{Fore.GREEN}✅ Orphaned models generated: {filepath}{Style.RESET_ALL}")
                        if debug_mode:
                            print(f"✅ Command.handle: Orphaned models report generated: {filepath}")
                else:
                    self.stdout.write(f"{Fore.YELLOW}ℹ️  No orphaned tables found to generate models for{Style.RESET_ALL}")
                    if debug_mode:
                        print(f"ℹ️ Command.handle: No orphaned tables found")
            
            if debug_mode:
                print(f"✅ Command.handle: Command execution completed successfully")
            self.stdout.write(f"{Fore.GREEN}Synchronization completed!{Style.RESET_ALL}")
            
            # Show txt-log success message
            if options['txt_log']:
                # Get the actual file path that was used
                if os.path.dirname(options['txt_log']) == '':
                    output_dir = get_setting('REPORT_OUTPUT_DIR', 'dbsync_reports/')
                    log_file_path = os.path.join(output_dir, options['txt_log'])
                else:
                    log_file_path = options['txt_log']
                self.stdout.write(f"{Fore.CYAN}📝 Terminal output saved to: {log_file_path}{Style.RESET_ALL}")
            
        except Exception as e:
            error_msg = f"❌ Synchronization failed: {e}"
            if debug_mode:
                print(f"❌ Command.handle: {error_msg}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
            self.stdout.write(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
            raise CommandError(error_msg)
        finally:
            # Cleanup txt-log file handling
            if log_file:
                try:
                    sys.stdout = original_stdout
                    log_file.close()
                    if debug_mode:
                        print(f"✅ Command.handle: Text log file closed successfully")
                except Exception as e:
                    if debug_mode:
                        print(f"❌ Command.handle: Error closing log file: {e}")
    
    def _display_results(self, results):
        """
        Display synchronization results to the user
        
        This method formats and displays the results of the synchronization process,
        including success, warning, and error messages for each model processed.
        
        Args:
            results (dict): Dictionary containing sync results for each model
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 Command._display_results: Displaying sync results for {len(results)} models")
        
        self.stdout.write(f"\n{Fore.CYAN}Sync Results:{Style.RESET_ALL}")
        self.stdout.write("-" * 30)
        
        success_count = 0
        warning_count = 0
        error_count = 0
        skipped_count = 0
        
        for model_name, result in results.items():
            if debug_mode:
                print(f"   Processing result for model: {model_name} (status: {result.get('status', 'unknown')})")
            
            if result['status'] == 'success':
                color = Fore.GREEN
                status = "✅"
                success_count += 1
            elif result['status'] == 'warning':
                color = Fore.YELLOW  
                status = "⚠️"
                warning_count += 1
            elif result['status'] == 'skipped':
                color = Fore.BLUE
                status = "⏭️"
                skipped_count += 1
            else:
                color = Fore.RED
                status = "❌"
                error_count += 1
            
            self.stdout.write(f"{status} {color}{model_name}{Style.RESET_ALL}")
            
            for action in result.get('actions', []):
                self.stdout.write(f"   - {action}")
            
            # Display warnings
            for warning in result.get('warnings', []):
                self.stdout.write(f"   {Fore.YELLOW}⚠️  {warning}{Style.RESET_ALL}")
            
            # Display errors
            for error in result.get('errors', []):
                self.stdout.write(f"   {Fore.RED}❌ {error}{Style.RESET_ALL}")
        
        if debug_mode:
            print(f"✅ Command._display_results: Displayed results summary:")
            print(f"   Success: {success_count}, Warnings: {warning_count}, Errors: {error_count}, Skipped: {skipped_count}")
    
    def _display_retry_results(self, failed_operations):
        """
        Display retry results for failed operations
        
        Args:
            failed_operations (list): List of failed operations that couldn't be retried successfully
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 Command._display_retry_results: Displaying {len(failed_operations)} failed operations")
        
        if failed_operations:
            self.stdout.write(f"\n{Fore.RED}Failed Operations After Retry:{Style.RESET_ALL}")
            self.stdout.write("-" * 40)
            
            for failed_op in failed_operations:
                operation_type = failed_op['type']
                table_name = failed_op['table_name']
                error = failed_op['error']
                attempts = failed_op['attempts']
                
                self.stdout.write(f"❌ {Fore.RED}{operation_type.upper()}{Style.RESET_ALL} on {Fore.CYAN}{table_name}{Style.RESET_ALL}")
                self.stdout.write(f"   Attempts: {attempts}")
                self.stdout.write(f"   Error: {error}")
                self.stdout.write("")
            
            self.stdout.write(f"{Fore.YELLOW}⚠️  These operations failed after maximum retry attempts{Style.RESET_ALL}")
            self.stdout.write(f"{Fore.CYAN}💡 Consider fixing the underlying issues and running the sync again{Style.RESET_ALL}")
            
            if debug_mode:
                print(f"✅ Command._display_retry_results: Displayed {len(failed_operations)} failed operations")
        else:
            self.stdout.write(f"\n{Fore.GREEN}✅ All operations completed successfully after retry!{Style.RESET_ALL}")
            if debug_mode:
                print(f"✅ Command._display_retry_results: All operations successful")
    
    def _display_orphaned_tables(self, orphaned_tables):
        """
        Display orphaned tables information
        
        This method shows the user which tables exist in the database but don't
        have corresponding Django models.
        
        Args:
            orphaned_tables (list): List of orphaned table dictionaries with details
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 Command._display_orphaned_tables: Displaying {len(orphaned_tables)} orphaned tables")
        
        if orphaned_tables:
            self.stdout.write(f"\n{Fore.YELLOW}Orphaned Tables:{Style.RESET_ALL}")
            self.stdout.write("-" * 30)
            
            total_rows = 0
            total_size = 0
            
            for table in orphaned_tables:
                # Handle both string and dictionary formats for backward compatibility
                if isinstance(table, dict):
                    table_name = table['name']
                    rows = table.get('rows', 0)
                    size_mb = table.get('size_mb', 0)
                    columns = table.get('columns', 0)
                    
                    # Add to totals
                    if isinstance(rows, (int, float)):
                        total_rows += rows
                    if isinstance(size_mb, (int, float)):
                        total_size += size_mb
                    
                    # Format size display
                    if isinstance(size_mb, (int, float)):
                        if size_mb > 100:
                            size_display = f"{Fore.RED}{size_mb:.2f} MB{Style.RESET_ALL}"
                        elif size_mb > 10:
                            size_display = f"{Fore.YELLOW}{size_mb:.2f} MB{Style.RESET_ALL}"
                        else:
                            size_display = f"{Fore.GREEN}{size_mb:.2f} MB{Style.RESET_ALL}"
                    else:
                        size_display = f"{size_mb}"
                    
                    # Format row count display
                    if isinstance(rows, (int, float)):
                        if rows > 10000:
                            row_display = f"{Fore.RED}{rows:,}{Style.RESET_ALL}"
                        elif rows > 1000:
                            row_display = f"{Fore.YELLOW}{rows:,}{Style.RESET_ALL}"
                        else:
                            row_display = f"{Fore.GREEN}{rows:,}{Style.RESET_ALL}"
                    else:
                        row_display = f"{rows}"
                    
                    self.stdout.write(f"   - {Fore.CYAN}{table_name}{Style.RESET_ALL} "
                                    f"(rows: {row_display}, size: {size_display}, columns: {columns})")
                else:
                    # Backward compatibility for string format
                    self.stdout.write(f"   - {Fore.CYAN}{table}{Style.RESET_ALL}")
            
            # Show summary if we have detailed data
            if any(isinstance(table, dict) for table in orphaned_tables):
                self.stdout.write(f"\n{Fore.BLUE}Summary:{Style.RESET_ALL}")
                self.stdout.write(f"   Total Tables: {len(orphaned_tables)}")
                if isinstance(total_rows, (int, float)) and total_rows > 0:
                    self.stdout.write(f"   Total Rows: {total_rows:,}")
                if isinstance(total_size, (int, float)) and total_size > 0:
                    self.stdout.write(f"   Total Size: {total_size:.2f} MB")
            
            if debug_mode:
                print(f"✅ Command._display_orphaned_tables: Displayed {len(orphaned_tables)} orphaned tables")
        else:
            self.stdout.write(f"\n{Fore.GREEN}✅ No orphaned tables found!{Style.RESET_ALL}")
            if debug_mode:
                print(f"ℹ️ Command._display_orphaned_tables: No orphaned tables found")
    
    def _handle_orphaned_tables(self, sync_engine, orphaned_tables, dry_run):
        """
        Handle orphaned tables (drop them if requested)
        
        This method processes orphaned tables by either dropping them or showing
        what would be dropped in dry run mode.
        
        Args:
            sync_engine (SyncEngine): The sync engine instance
            orphaned_tables (list): List of orphaned table dictionaries with details
            dry_run (bool): Whether to perform dry run mode
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 Command._handle_orphaned_tables: Handling {len(orphaned_tables)} orphaned tables (dry_run: {dry_run})")
        
        if not orphaned_tables:
            self.stdout.write(f"{Fore.GREEN}✅ No orphaned tables found!{Style.RESET_ALL}")
            if debug_mode:
                print(f"ℹ️ Command._handle_orphaned_tables: No orphaned tables to handle")
            return
        
        self.stdout.write(f"{Fore.BLUE}Found {len(orphaned_tables)} orphaned tables:{Style.RESET_ALL}")
        
        # Calculate totals for display
        total_rows = 0
        total_size = 0
        
        for table in orphaned_tables:
            # Handle both string and dictionary formats for backward compatibility
            if isinstance(table, dict):
                table_name = table['name']
                rows = table.get('rows', 0)
                size_mb = table.get('size_mb', 0)
                columns = table.get('columns', 0)
                
                # Add to totals
                if isinstance(rows, (int, float)):
                    total_rows += rows
                if isinstance(size_mb, (int, float)):
                    total_size += size_mb
                
                # Format size display
                if isinstance(size_mb, (int, float)):
                    if size_mb > 100:
                        size_display = f"{Fore.RED}{size_mb:.2f} MB{Style.RESET_ALL}"
                    elif size_mb > 10:
                        size_display = f"{Fore.YELLOW}{size_mb:.2f} MB{Style.RESET_ALL}"
                    else:
                        size_display = f"{Fore.GREEN}{size_mb:.2f} MB{Style.RESET_ALL}"
                else:
                    size_display = f"{size_mb}"
                
                # Format row count display
                if isinstance(rows, (int, float)):
                    if rows > 10000:
                        row_display = f"{Fore.RED}{rows:,}{Style.RESET_ALL}"
                    elif rows > 1000:
                        row_display = f"{Fore.YELLOW}{rows:,}{Style.RESET_ALL}"
                    else:
                        row_display = f"{Fore.GREEN}{rows:,}{Style.RESET_ALL}"
                else:
                    row_display = f"{rows}"
                
                self.stdout.write(f"   - {Fore.CYAN}{table_name}{Style.RESET_ALL} "
                                f"(rows: {row_display}, size: {size_display}, columns: {columns})")
            else:
                # Backward compatibility for string format
                self.stdout.write(f"   - {Fore.CYAN}{table}{Style.RESET_ALL}")
        
        # Show summary if we have detailed data
        if any(isinstance(table, dict) for table in orphaned_tables):
            self.stdout.write(f"\n{Fore.BLUE}Summary:{Style.RESET_ALL}")
            self.stdout.write(f"   Total Tables: {len(orphaned_tables)}")
            if isinstance(total_rows, (int, float)) and total_rows > 0:
                self.stdout.write(f"   Total Rows: {total_rows:,}")
            if isinstance(total_size, (int, float)) and total_size > 0:
                self.stdout.write(f"   Total Size: {total_size:.2f} MB")
        
        if dry_run:
            self.stdout.write(f"\n{Fore.YELLOW}⚠️  DRY RUN: Would drop {len(orphaned_tables)} orphaned tables{Style.RESET_ALL}")
            if debug_mode:
                print(f"ℹ️ Command._handle_orphaned_tables: Dry run mode - would drop {len(orphaned_tables)} tables")
        else:
            # Ask for confirmation
            response = input(f"\n{Fore.RED}⚠️  Are you sure you want to drop {len(orphaned_tables)} orphaned tables? (yes/no): {Style.RESET_ALL}")
            if response.lower() in ['yes', 'y']:
                if debug_mode:
                    print(f"🔍 Command._handle_orphaned_tables: User confirmed dropping {len(orphaned_tables)} tables")
                
                self.stdout.write(f"{Fore.YELLOW}Dropping orphaned tables...{Style.RESET_ALL}")
                dropped_count = 0
                
                for table in orphaned_tables:
                    try:
                        # Extract table name from dictionary or use string directly
                        if isinstance(table, dict):
                            table_name = table['name']
                        else:
                            table_name = table
                        
                        sync_engine.drop_orphaned_table(table_name)
                        self.stdout.write(f"   ✅ Dropped: {table_name}")
                        dropped_count += 1
                        if debug_mode:
                            print(f"   ✅ Successfully dropped table: {table_name}")
                    except Exception as e:
                        # Extract table name for error message
                        if isinstance(table, dict):
                            table_name = table['name']
                        else:
                            table_name = table
                        
                        error_msg = f"Failed to drop {table_name}: {e}"
                        self.stdout.write(f"   ❌ {error_msg}")
                        if debug_mode:
                            print(f"   ❌ Failed to drop table {table_name}: {e}")
                
                self.stdout.write(f"{Fore.GREEN}✅ Successfully dropped {dropped_count}/{len(orphaned_tables)} orphaned tables{Style.RESET_ALL}")
                if debug_mode:
                    print(f"✅ Command._handle_orphaned_tables: Successfully dropped {dropped_count}/{len(orphaned_tables)} tables")
            else:
                self.stdout.write(f"{Fore.YELLOW}⚠️  Orphaned tables not dropped{Style.RESET_ALL}")
                if debug_mode:
                    print(f"ℹ️ Command._handle_orphaned_tables: User cancelled dropping orphaned tables")
    
    def _generate_report(self, results, report_type):
        """
        Generate HTML or JSON report of synchronization results
        
        This method creates detailed reports of the synchronization process,
        including all operations performed, warnings, and errors.
        
        Args:
            results (dict): Dictionary containing sync results
            report_type (str): Type of report to generate ('json', 'html', or 'both')
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 Command._generate_report: Generating {report_type} report")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = get_setting('REPORT_OUTPUT_DIR', 'dbsync_reports/')
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        if report_type in ['json', 'both']:
            if debug_mode:
                print(f"   Generating JSON report")
            json_file = os.path.join(output_dir, f'dbsync_report_{timestamp}.json')
            with open(json_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            self.stdout.write(f"{Fore.GREEN}✅ JSON report generated: {json_file}{Style.RESET_ALL}")
            if debug_mode:
                print(f"   ✅ JSON report saved to: {json_file}")
        
        if report_type in ['html', 'both']:
            if debug_mode:
                print(f"   Generating HTML report")
            html_file = os.path.join(output_dir, f'dbsync_report_{timestamp}.html')
            self._generate_html_report(results, html_file, timestamp)
            self.stdout.write(f"{Fore.GREEN}✅ HTML report generated: {html_file}{Style.RESET_ALL}")
            if debug_mode:
                print(f"   ✅ HTML report saved to: {html_file}")
        
        if debug_mode:
            print(f"✅ Command._generate_report: Successfully generated {report_type} report")
    
    def _generate_html_report(self, results, html_file, timestamp):
        """
        Generate detailed HTML report of synchronization results
        
        This method creates a comprehensive HTML report with styling and
        detailed information about the synchronization process.
        
        Args:
            results (dict): Dictionary containing sync results
            html_file (str): Path to save the HTML file
            timestamp (str): Timestamp for the report
        """
        debug_mode = get_setting('DEBUG_MODE')
        if debug_mode:
            print(f"🔍 Command._generate_html_report: Generating HTML report to {html_file}")
        
        # Calculate statistics
        total_models = len(results)
        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        warning_count = sum(1 for r in results.values() if r['status'] == 'warning')
        error_count = sum(1 for r in results.values() if r['status'] == 'error')
        skipped_count = sum(1 for r in results.values() if r['status'] == 'skipped')
        
        if debug_mode:
            print(f"   Report statistics: Total={total_models}, Success={success_count}, Warnings={warning_count}, Errors={error_count}, Skipped={skipped_count}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Django DB Sync Report - {timestamp}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f8f9fa;
                    color: #333;
                    margin: 0;
                    padding: 0 20px 50px;
                }}
                .container {{
                    max-width: 900px;
                    margin: auto;
                }}
                .header {{
                    background: linear-gradient(135deg, #007BFF, #00C6FF);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-top: 20px;
                }}
                .header h1 {{
                    margin: 0 0 10px;
                }}
                .summary {{
                    margin: 30px 0;
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                }}
                .summary-boxes {{
                    display: flex;
                    gap: 15px;
                    flex-wrap: wrap;
                }}
                .summary-box {{
                    flex: 1;
                    min-width: 120px;
                    background-color: #f1f3f5;
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                }}
                .summary-box.success {{ border-left: 5px solid #28a745; }}
                .summary-box.warning {{ border-left: 5px solid #ffc107; }}
                .summary-box.error {{ border-left: 5px solid #dc3545; }}
                .summary-box.skipped {{ border-left: 5px solid #17a2b8; }}
                .model {{
                    margin: 20px 0;
                    padding: 20px;
                    background-color: #fff;
                    border-left: 6px solid #ccc;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                }}
                .model.success {{ border-left-color: #28a745; }}
                .model.warning {{ border-left-color: #ffc107; }}
                .model.error {{ border-left-color: #dc3545; }}
                .model.skipped {{ border-left-color: #17a2b8; }}
                .action, .warning-msg, .error-msg {{
                    margin: 5px 0;
                    padding: 10px;
                    border-radius: 5px;
                }}
                .action {{ background-color: #e9ecef; }}
                .warning-msg {{ background-color: #fff3cd; color: #856404; }}
                .error-msg {{ background-color: #f8d7da; color: #721c24; }}
                h2, h3, h4 {{ margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Django DB Sync Report</h1>
                    <p>Generated on: {timestamp}</p>
                    <p>Powered by: <strong>Love Dazzell</strong></p>
                </div>

                <div class="summary">
                    <h2>Summary</h2>
                    <div class="summary-boxes">
                        <div class="summary-box success">
                            ✅ Successful<br><strong>{success_count}</strong>
                        </div>
                        <div class="summary-box warning">
                            ⚠️ Warnings<br><strong>{warning_count}</strong>
                        </div>
                        <div class="summary-box error">
                            ❌ Errors<br><strong>{error_count}</strong>
                        </div>
                        <div class="summary-box skipped">
                            ⏭️ Skipped<br><strong>{skipped_count}</strong>
                        </div>
                        <div class="summary-box">
                            📦 Total Models<br><strong>{total_models}</strong>
                        </div>
                    </div>
                </div>

                <h2>Detailed Results</h2>
        """

        for model_name, result in results.items():
            status_class = result['status']
            status_icon = {
                'success': '✅',
                'warning': '⚠️',
                'error': '❌',
                'skipped': '⏭️'
            }.get(result['status'], '❓')

            html_content += f"""
                <div class="model {status_class}">
                    <h3>{status_icon} {model_name}</h3>
                    <p><strong>Status:</strong> {result['status'].title()}</p>
            """

            if result.get('actions'):
                html_content += '<h4>Actions:</h4>'
                for action in result['actions']:
                    html_content += f'<div class="action">- {action}</div>'

            if result.get('warnings'):
                html_content += '<h4>Warnings:</h4>'
                for warning in result['warnings']:
                    html_content += f'<div class="warning-msg">⚠️ {warning}</div>'

            if result.get('errors'):
                html_content += '<h4>Errors:</h4>'
                for error in result['errors']:
                    html_content += f'<div class="error-msg">❌ {error}</div>'

            html_content += '</div>'

        html_content += """
            </div>
        </body>
        </html>
        """
        
#         html_content = f"""
# <!DOCTYPE html>
# <html>
# <head>
#     <title>Django DB Sync Report - {timestamp}</title>
#     <style>
#         body {{ font-family: Arial, sans-serif; margin: 20px; }}
#         .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
#         .summary {{ margin: 20px 0; }}
#         .model {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
#         .success {{ border-left-color: #4CAF50; }}
#         .warning {{ border-left-color: #FF9800; }}
#         .error {{ border-left-color: #F44336; }}
#         .skipped {{ border-left-color: #2196F3; }}
#         .action {{ margin: 5px 0; padding: 5px; background-color: #f9f9f9; }}
#         .warning-msg {{ color: #FF9800; }}
#         .error-msg {{ color: #F44336; }}
#     </style>
# </head>
# <body>
#     <div class="header">
#         <h1>Django DB Sync Report</h1>
#         <p>Generated on: {timestamp}</p>
#         <p>Powerd by: Love Dazzell</p>
#     </div>
    
#     <div class="summary">
#         <h2>Summary</h2>
#         <p>Total Models: {total_models}</p>
#         <p>✅ Successful: {success_count}</p>
#         <p>⚠️  Warnings: {warning_count}</p>
#         <p>❌ Errors: {error_count}</p>
#         <p>⏭️  Skipped: {skipped_count}</p>
#     </div>
    
#     <h2>Detailed Results</h2>
# """
        
#         for model_name, result in results.items():
#             status_class = result['status']
#             status_icon = {
#                 'success': '✅',
#                 'warning': '⚠️',
#                 'error': '❌',
#                 'skipped': '⏭️'
#             }.get(result['status'], '❓')
            
#             html_content += f"""
#     <div class="model {status_class}">
#         <h3>{status_icon} {model_name}</h3>
#         <p><strong>Status:</strong> {result['status'].title()}</p>
# """
            
#             # Add actions
#             if result.get('actions'):
#                 html_content += '<h4>Actions:</h4>'
#                 for action in result['actions']:
#                     html_content += f'<div class="action">- {action}</div>'
            
#             # Add warnings
#             if result.get('warnings'):
#                 html_content += '<h4>Warnings:</h4>'
#                 for warning in result['warnings']:
#                     html_content += f'<div class="warning-msg">⚠️  {warning}</div>'
            
#             # Add errors
#             if result.get('errors'):
#                 html_content += '<h4>Errors:</h4>'
#                 for error in result['errors']:
#                     html_content += f'<div class="error-msg">❌ {error}</div>'
            
#             html_content += '</div>'
        
#         html_content += """
# </body>
# </html>
# """
        
        # with open(html_file, 'w') as f:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        if debug_mode:
            print(f"✅ Command._generate_html_report: HTML report generated successfully")
