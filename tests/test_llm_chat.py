import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to the Python path to allow module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules import llm_chat

class TestLLMChat(unittest.TestCase):

    def setUp(self):
        # Reset chat history before each test
        llm_chat.chat_history = [
            {"role": "system", "content": "You are a helpful AI assistant."},
        ]

    @patch('modules.llm_chat.client.chat.completions.create')
    def test_handle_success(self, mock_create):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].delta.content = "Hello there!"
        mock_create.return_value = [mock_response]

        # Call the function
        response = llm_chat.handle("chat Hello")

        # Assertions
        self.assertEqual(response, "Hello there!")
        self.assertEqual(len(llm_chat.chat_history), 3) # System, User, Assistant
        self.assertEqual(llm_chat.chat_history[1]['role'], 'user')
        self.assertEqual(llm_chat.chat_history[1]['content'], 'Hello')
        self.assertEqual(llm_chat.chat_history[2]['role'], 'assistant')
        self.assertEqual(llm_chat.chat_history[2]['content'], 'Hello there!')

    def test_handle_empty_input(self):
        response = llm_chat.handle("chat ")
        self.assertEqual(response, "Please provide something to chat about.")

    @patch('modules.llm_chat.client.chat.completions.create')
    def test_handle_api_error(self, mock_create):
        # Mock an API error
        mock_create.side_effect = Exception("API Error")

        # Call the function
        response = llm_chat.handle("chat test")

        # Assertions
        self.assertIn("An error occurred", response)

if __name__ == '__main__':
    unittest.main()
