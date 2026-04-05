import unittest
from unittest.mock import MagicMock, patch
from io import StringIO
import logging

# Import the functions we want to test
from empty_trash import batch_delete_messages, empty_trash

class TestEmptyTrash(unittest.TestCase):

    def setUp(self):
        # Suppress logging during tests
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        # Re-enable logging
        logging.disable(logging.NOTSET)

    @patch('empty_trash.logger')
    def test_batch_delete_messages(self, mock_logger):
        mock_service = MagicMock()
        # Mock the chain of calls: service.users().messages().batchDelete().execute()
        mock_batch_delete = mock_service.users().messages().batchDelete
        
        # Test with 1500 messages to check batching (limit is 1000)
        message_ids = [f'id_{i}' for i in range(1500)]
        
        batch_delete_messages(mock_service, message_ids)
        
        # Should be called twice (1000 + 500)
        self.assertEqual(mock_batch_delete.call_count, 2)
        
        # Verify first batch
        args, kwargs = mock_batch_delete.call_args_list[0]
        self.assertEqual(kwargs['body']['ids'], message_ids[:1000])
        
        # Verify second batch
        args, kwargs = mock_batch_delete.call_args_list[1]
        self.assertEqual(kwargs['body']['ids'], message_ids[1000:])

    @patch('empty_trash.build')
    @patch('empty_trash.get_credentials')
    @patch('empty_trash.batch_delete_messages')
    def test_empty_trash_pagination(self, mock_batch_delete, mock_get_creds, mock_build):
        # Mock credentials and service
        mock_get_creds.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Mock list() to return two pages
        mock_list = mock_service.users().messages().list
        mock_list.side_effect = [
            # Page 1
            MagicMock(execute=MagicMock(return_value={
                'messages': [{'id': 'id1'}, {'id': 'id2'}],
                'nextPageToken': 'token1'
            })),
            # Page 2
            MagicMock(execute=MagicMock(return_value={
                'messages': [{'id': 'id3'}],
                # No nextPageToken
            }))
        ]
        
        empty_trash(dry_run=False)
        
        # Check that list was called twice
        self.assertEqual(mock_list.call_count, 2)
        
        # Check that batch_delete_messages was called with all 3 IDs
        mock_batch_delete.assert_called_once()
        args, kwargs = mock_batch_delete.call_args
        self.assertEqual(args[1], ['id1', 'id2', 'id3'])

    @patch('empty_trash.build')
    @patch('empty_trash.get_credentials')
    @patch('empty_trash.batch_delete_messages')
    def test_empty_trash_dry_run(self, mock_batch_delete, mock_get_creds, mock_build):
        # Mock credentials and service
        mock_get_creds.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Mock list() to return some messages
        mock_list = mock_service.users().messages().list
        mock_list.return_value.execute.return_value = {
            'messages': [{'id': 'id1'}]
        }
        
        # Run with dry_run=True
        empty_trash(dry_run=True)
        
        # batch_delete_messages should NOT be called
        mock_batch_delete.assert_not_called()

if __name__ == '__main__':
    unittest.main()
