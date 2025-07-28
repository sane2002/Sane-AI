
import unittest
from unittest.mock import patch, mock_open
import json
import sys
import os

# Add the parent directory to the Python path to allow module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules import knowledge_base

class TestKnowledgeBase(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_remember_new_item(self, mock_file):
        response = knowledge_base.handle("remember my favorite color is blue")
        self.assertEqual(response, "I will remember that: 'my favorite color is blue'")
        mock_file().write.assert_called()

    @patch('builtins.open', new_callable=mock_open, read_data='[{"timestamp": "2024-07-28 12:00:00", "data": "my favorite color is blue"}]')
    def test_recall_all(self, mock_file):
        response = knowledge_base.handle("recall")
        self.assertIn("Here are all my memories:", response)
        self.assertIn("- my favorite color is blue", response)

    @patch('builtins.open', new_callable=mock_open, read_data='[{"timestamp": "2024-07-28 12:00:00", "data": "my favorite color is blue"}]')
    def test_recall_specific(self, mock_file):
        response = knowledge_base.handle("recall color")
        self.assertIn("Here's what I found:", response)
        self.assertIn("- my favorite color is blue", response)

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_recall_not_found(self, mock_file):
        response = knowledge_base.handle("recall python")
        self.assertEqual(response, "I couldn't find any memories related to 'python'.")

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_remember_empty(self, mock_file):
        response = knowledge_base.handle("remember ")
        self.assertEqual(response, "What should I remember?")

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_recall_empty(self, mock_file):
        response = knowledge_base.handle("recall ")
        self.assertEqual(response, "I don't have any memories yet.")

    def test_unknown_action(self):
        response = knowledge_base.handle("unknown action")
        self.assertEqual(response, "I'm not sure how to handle that.")

if __name__ == '__main__':
    unittest.main()
