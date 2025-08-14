import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.db import models

from django_dbsync.core.sync_engine import SyncEngine
from django_dbsync.utils.helpers import detect_table_case_mismatches


class MockModel:
    """Mock Django model for testing"""
    class Meta:
        app_label = 'management'
        db_table = 'MemberLicense'
    
    _meta = Meta()
    __name__ = 'MemberLicense'


class TableCaseHandlingTest(TestCase):
    """Test table name case handling functionality"""
    
    def setUp(self):
        self.sync_engine = SyncEngine(dry_run=True, auto_approve=True)
    
    def test_find_existing_table_for_model_case_mismatch(self):
        """Test that case mismatches are detected correctly"""
        # Mock the database inspector to return a table with different case
        with patch.object(self.sync_engine.inspector, 'get_existing_tables') as mock_get_tables:
            mock_get_tables.return_value = ['memberlicense']  # lowercase in DB
            
            model = MockModel()
            existing_table, rename_target = self.sync_engine.find_existing_table_for_model(model)
            
            # Should detect the case mismatch
            self.assertEqual(existing_table, 'memberlicense')
            self.assertEqual(rename_target, 'MemberLicense')
    
    def test_find_existing_table_for_model_case_match(self):
        """Test that matching case returns no rename target"""
        # Mock the database inspector to return a table with matching case
        with patch.object(self.sync_engine.inspector, 'get_existing_tables') as mock_get_tables:
            mock_get_tables.return_value = ['MemberLicense']  # matching case
            
            model = MockModel()
            existing_table, rename_target = self.sync_engine.find_existing_table_for_model(model)
            
            # Should not need renaming
            self.assertEqual(existing_table, 'MemberLicense')
            self.assertIsNone(rename_target)
    
    def test_detect_table_case_mismatches(self):
        """Test the helper function for detecting mismatches"""
        with patch('django_dbsync.utils.helpers.connections') as mock_connections:
            # Mock the database connection
            mock_connection = MagicMock()
            mock_connection.introspection.table_names.return_value = ['memberlicense']
            mock_connections.__getitem__.return_value = mock_connection
            
            # Mock Django apps
            with patch('django_dbsync.utils.helpers.apps') as mock_apps:
                mock_app_config = MagicMock()
                mock_app_config.get_models.return_value = [MockModel()]
                mock_apps.get_app_configs.return_value = [mock_app_config]
                
                mismatches = detect_table_case_mismatches()
                
                # Should find the mismatch
                self.assertIn('management.MemberLicense', mismatches)
                mismatch_info = mismatches['management.MemberLicense']
                self.assertEqual(mismatch_info['expected_table'], 'MemberLicense')
                self.assertEqual(mismatch_info['actual_table'], 'memberlicense')
                self.assertEqual(mismatch_info['type'], 'case_mismatch')


if __name__ == '__main__':
    unittest.main() 