"""
تست‌های کلاس Client
Tests for Client class
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# اضافه کردن مسیر پروژه به sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from robka import Client
from robka.exceptions import AuthenticationError, NetworkError


class TestClient(unittest.TestCase):
    """تست‌های کلاس Client"""
    
    def setUp(self):
        """تنظیمات اولیه تست"""
        self.valid_auth = "a" * 32  # توکن معتبر 32 کاراکتری
        self.invalid_auth = "invalid_token"
        
    def test_valid_auth_token(self):
        """تست توکن معتبر"""
        client = Client(self.valid_auth)
        self.assertEqual(client.auth, self.valid_auth)
        
    def test_invalid_auth_token(self):
        """تست توکن نامعتبر"""
        with self.assertRaises(AuthenticationError):
            Client(self.invalid_auth)
            
    def test_empty_auth_token(self):
        """تست توکن خالی"""
        with self.assertRaises(AuthenticationError):
            Client("")
            
    def test_none_auth_token(self):
        """تست توکن None"""
        with self.assertRaises(AuthenticationError):
            Client(None)
    
    def test_client_initialization(self):
        """تست مقداردهی اولیه کلاینت"""
        client = Client(self.valid_auth, timeout=60)
        
        self.assertEqual(client.auth, self.valid_auth)
        self.assertEqual(client.timeout, 60)
        self.assertFalse(client.running)
        self.assertEqual(len(client.message_handlers), 0)
    
    def test_message_handler_decorator(self):
        """تست دکوراتور مدیریت پیام"""
        client = Client(self.valid_auth)
        
        @client.on_message()
        def test_handler(message):
            return "handled"
        
        self.assertEqual(len(client.message_handlers), 1)
        handler_func, filters = client.message_handlers[0]
        self.assertEqual(handler_func, test_handler)
    
    @patch('robka.client.requests.Session.post')
    def test_send_message_success(self, mock_post):
        """تست ارسال پیام موفق"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data_enc': 'encrypted_response'}
        mock_post.return_value = mock_response
        
        client = Client(self.valid_auth)
        
        # Mock encryption
        with patch.object(client.encryption, 'encrypt') as mock_encrypt, \
             patch.object(client.encryption, 'decrypt') as mock_decrypt:
            
            mock_encrypt.return_value = 'encrypted_data'
            mock_decrypt.return_value = '{"status": "OK", "data": {"message_id": "123"}}'
            
            result = client.send_message("chat123", "سلام")
            
            self.assertIsNotNone(result)
            mock_post.assert_called_once()
    
    @patch('robka.client.requests.Session.post')
    def test_send_message_network_error(self, mock_post):
        """تست خطای شبکه در ارسال پیام"""
        mock_post.side_effect = Exception("Network error")
        
        client = Client(self.valid_auth)
        
        with self.assertRaises(NetworkError):
            client.send_message("chat123", "سلام")
    
    def test_stop_method(self):
        """تست متد توقف ربات"""
        client = Client(self.valid_auth)
        client.running = True
        
        client.stop()
        
        self.assertFalse(client.running)


if __name__ == '__main__':
    unittest.main()

