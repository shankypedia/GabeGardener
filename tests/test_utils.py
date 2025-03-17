"""
Tests for utility functionality.
"""
import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from steamtime.utils.crypto import encrypt_password, decrypt_password
from steamtime.utils.file_manager import get_config_dir, get_login_keys_dir, save_login_key, load_login_key
from steamtime.utils.stats import load_stats, save_stats, update_account_stats, update_game_stats

class TestCrypto(unittest.TestCase):
    """Test cases for cryptography utilities."""
    
    def test_encrypt_decrypt(self):
        """Test encrypting and decrypting passwords."""
        # Test with a simple password
        password = "test_password"
        encrypted = encrypt_password(password)
        decrypted = decrypt_password(encrypted)
        
        self.assertNotEqual(password, encrypted)
        self.assertEqual(password, decrypted)
        
        # Test with a complex password
        password = "C0mpl3x!P@ssw0rd#123"
        encrypted = encrypt_password(password)
        decrypted = decrypt_password(encrypted)
        
        self.assertNotEqual(password, encrypted)
        self.assertEqual(password, decrypted)
        
        # Test with an empty password
        password = ""
        encrypted = encrypt_password(password)
        decrypted = decrypt_password(encrypted)
        
        self.assertNotEqual(password, encrypted)
        self.assertEqual(password, decrypted)

class TestFileManager(unittest.TestCase):
    """Test cases for file management utilities."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for config
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = self.temp_dir.name
        
        # Patch environment variables
        self.env_patcher = patch.dict('os.environ', {
            'GABEGARDENER_CONFIG_DIR': self.config_dir
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
        self.temp_dir.cleanup()
    
    def test_get_config_dir(self):
        """Test getting the configuration directory."""
        config_dir = get_config_dir()
        self.assertEqual(config_dir, self.config_dir)
        self.assertTrue(os.path.exists(config_dir))
    
    def test_get_login_keys_dir(self):
        """Test getting the login keys directory."""
        login_keys_dir = get_login_keys_dir()
        expected_dir = os.path.join(self.config_dir, "login_keys")
        self.assertEqual(login_keys_dir, expected_dir)
        self.assertTrue(os.path.exists(login_keys_dir))
    
    def test_save_load_login_key(self):
        """Test saving and loading login keys."""
        username = "test_user"
        login_key = "test_login_key"
        
        # Save the login key
        save_login_key(username, login_key)
        
        # Check that the file exists
        login_key_file = os.path.join(get_login_keys_dir(), f"{username}.key")
        self.assertTrue(os.path.exists(login_key_file))
        
        # Load the login key
        loaded_key = load_login_key(username)
        self.assertEqual(loaded_key, login_key)
        
        # Test loading a non-existent key
        non_existent_key = load_login_key("non_existent_user")
        self.assertIsNone(non_existent_key)

class TestStats(unittest.TestCase):
    """Test cases for statistics utilities."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for config
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = self.temp_dir.name
        
        # Patch environment variables
        self.env_patcher = patch.dict('os.environ', {
            'GABEGARDENER_CONFIG_DIR': self.config_dir
        })
        self.env_patcher.start()
        
        # Create stats directory
        os.makedirs(os.path.join(self.config_dir, "stats"), exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
        self.temp_dir.cleanup()
    
    def test_load_default_stats(self):
        """Test loading default statistics."""
        stats = load_stats()
        
        # Check that default structure is present
        self.assertIn("accounts", stats)
        self.assertIn("global", stats)
        self.assertIn("total_uptime", stats["global"])
        self.assertEqual(stats["global"]["total_messages"], 0)
        self.assertEqual(stats["global"]["total_logins"], 0)
    
    def test_save_load_stats(self):
        """Test saving and loading statistics."""
        # Create test stats
        stats = load_stats()
        stats["global"]["total_messages"] = 10
        stats["global"]["total_logins"] = 5
        
        # Save stats
        save_stats(stats)
        
        # Load stats
        loaded_stats = load_stats()
        
        # Check that values match
        self.assertEqual(loaded_stats["global"]["total_messages"], 10)
        self.assertEqual(loaded_stats["global"]["total_logins"], 5)
    
    def test_update_account_stats(self):
        """Test updating account statistics."""
        username = "test_user"
        
        # Update account stats
        update_account_stats(username, "messages_received", 3)
        update_account_stats(username, "logins")
        
        # Load stats
        stats = load_stats()
        
        # Check that account stats were updated
        self.assertIn(username, stats["accounts"])
        self.assertEqual(stats["accounts"][username]["messages_received"], 3)
        self.assertEqual(stats["accounts"][username]["logins"], 1)
        
        # Check that global stats were updated
        self.assertEqual(stats["global"]["total_messages"], 3)
        self.assertEqual(stats["global"]["total_logins"], 1)
    
    def test_update_game_stats(self):
        """Test updating game statistics."""
        username = "test_user"
        game_id = 730
        
        # Update game stats
        update_game_stats(username, game_id)
        update_game_stats(username, game_id)  # Update twice
        
        # Load stats
        stats = load_stats()
        
        # Check that game stats were updated
        self.assertIn(username, stats["accounts"])
        self.assertIn("games_played", stats["accounts"][username])
        self.assertIn(str(game_id), stats["accounts"][username]["games_played"])
        self.assertEqual(stats["accounts"][username]["games_played"][str(game_id)], 2)

if __name__ == '__main__':
    unittest.main()
