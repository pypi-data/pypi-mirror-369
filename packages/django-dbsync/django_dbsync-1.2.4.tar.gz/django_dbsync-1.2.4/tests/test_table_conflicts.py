import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase

from django_dbsync.core.sync_engine import SyncEngine
from django_dbsync.utils.helpers import detect_table_name_conflicts


class MockModel:
    """Mock Django model for testing"""
    class Meta:
        app_label = 'core'
        db_table = 'Publisher'
    
    _meta = Meta()
    __name__ = 'Publisher'


class TableConflictTest(TestCase):
    """Test table name conflict handling functionality"""
    
    def setUp(self):
        self.sync_engine = SyncEngine(dry_run=True, auto_approve=True)
    
    def test_find_existing_table_for_model_with_conflict(self):
        """Test that conflicts are detected and handled correctly"""
        # Mock the database inspector to return both lowercase and uppercase tables
        with patch.object(self.sync_engine.inspector, 'get_existing_tables') as mock_get_tables:
            mock_get_tables.return_value = ['publisher', 'Publisher']  # Both exist
            
            model = MockModel()
            existing_table, rename_target = self.sync_engine.find_existing_table_for_model(model)
            
            # Should detect the conflict and return the expected table as-is
            self.assertEqual(existing_table, 'Publisher')
            self.assertIsNone(rename_target)
    
    def test_find_existing_table_for_model_no_conflict(self):
        """Test that normal case mismatches work when no conflict exists"""
        # Mock the database inspector to return only lowercase table
        with patch.object(self.sync_engine.inspector, 'get_existing_tables') as mock_get_tables:
            mock_get_tables.return_value = ['publisher']  # Only lowercase exists
            
            model = MockModel()
            existing_table, rename_target = self.sync_engine.find_existing_table_for_model(model)
            
            # Should detect the case mismatch and propose rename
            self.assertEqual(existing_table, 'publisher')
            self.assertEqual(rename_target, 'Publisher')
    
    def test_detect_table_name_conflicts(self):
        """Test the helper function for detecting conflicts"""
        with patch('django_dbsync.utils.helpers.connections') as mock_connections:
            # Mock the database connection
            mock_connection = MagicMock()
            mock_connection.introspection.table_names.return_value = ['publisher', 'Publisher']
            mock_connections.__getitem__.return_value = mock_connection
            
            conflicts = detect_table_name_conflicts()
            
            # Should find the conflict
            self.assertIn('publisher', conflicts)
            conflict_info = conflicts['publisher']
            self.assertEqual(conflict_info['tables'], ['publisher', 'Publisher'])
            self.assertEqual(conflict_info['type'], 'case_conflict')
    
    def test_rename_table_safety_check(self):
        """Test that rename operation checks for existing target table"""
        # Mock the database inspector to return a table that would conflict
        with patch.object(self.sync_engine.inspector, 'get_existing_tables') as mock_get_tables:
            mock_get_tables.return_value = ['Publisher']  # Target already exists
            
            # Try to rename 'publisher' to 'Publisher' when 'Publisher' already exists
            result = self.sync_engine._rename_table('publisher', 'Publisher')
            
            # Should fail due to safety check
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main() 