"""
Tests for configuration functionality.
"""
import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from steamtime.config.settings import load_config, save_config, add_account, remove_account
from steamtime.config.default_config import DEFAULT_CONFIG

class TestConfig(unittest.TestCase):
    """Test cases for configuration functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for config
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = self.temp_dir.name
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # Patch environment variables
        self.env_patcher = patch.dict('os.environ', {
            'GABEGARDENER_CONFIG_DIR': self.config_dir,
            'GABEGARDENER_CONFIG': self.config_file
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
        self.temp_dir.cleanup()
    
    def test_load_default_config(self):
        """Test loading default configuration."""
        config = load_config()
        
        # Check that default values are present
        self.assertEqual(config["show_timer"], DEFAULT_CONFIG["show_timer"])
        self.assertEqual(config["language"], DEFAULT_CONFIG["language"])
        self.assertEqual(config["accounts"], [])
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        # Create a test config
        test_config = DEFAULT_CONFIG.copy()
        test_config["language"] = "es"
        test_config["accounts"] = [
            {
                "username": "test_user",
                "password": "test_password",
                "games": ["GabeGardener", 730]
            }
        ]
        
        # Save the config
        save_config(test_config)
        
        # Check that the file exists
        self.assertTrue(os.path.exists(self.config_file))
        
        # Load the config
        loaded_config = load_config()
        
        # Check that values match
        self.assertEqual(loaded_config["language"], "es")
        self.assertEqual(len(loaded_config["accounts"]), 1)
        self.assertEqual(loaded_config["accounts"][0]["username"], "test_user")
        
        # Password should be encrypted
        self.assertNotEqual(loaded_config["accounts"][0]["password"], "test_password")
        self.assertTrue(loaded_config["accounts"][0]["password"].startswith("enc:"))
    
    def test_add_account(self):
        """Test adding an account."""
        # Add an account
        add_account("test_user", "test_password", ["GabeGardener", 730])
        
        # Load the config
        config = load_config()
        
        # Check that the account was added
        self.assertEqual(len(config["accounts"]), 1)
        self.assertEqual(config["accounts"][0]["username"], "test_user")
        
        # Add another account
        add_account("test_user2", "test_password2", [440, 570])
        
        # Load the config
        config = load_config()
        
        # Check that both accounts are present
        self.assertEqual(len(config["accounts"]), 2)
        self.assertEqual(config["accounts"][1]["username"], "test_user2")
    
    def test_remove_account(self):
        """Test removing an account."""
        # Add accounts
        add_account("test_user", "test_password", ["GabeGardener", 730])
        add_account("test_user2", "test_password2", [440, 570])
        
        # Remove an account
        remove_account("test_user")
        
        # Load the config
        config = load_config()
        
        # Check that only one account remains
        self.assertEqual(len(config["accounts"]), 1)
        self.assertEqual(config["accounts"][0]["username"], "test_user2")
        
        # Remove the other account
        remove_account("test_user2")
        
        # Load the config
        config = load_config()
        
        # Check that no accounts remain
        self.assertEqual(len(config["accounts"]), 0)
    
    def test_update_existing_account(self):
        """Test updating an existing account."""
        # Add an account
        add_account("test_user", "test_password", ["GabeGardener", 730])
        
        # Update the account
        add_account("test_user", "new_password", ["GabeGardener", 440, 570])
        
        # Load the config
        config = load_config()
        
        # Check that the account was updated
        self.assertEqual(len(config["accounts"]), 1)
        self.assertEqual(config["accounts"][0]["username"], "test_user")
        self.assertEqual(len(config["accounts"][0]["games"]), 3)
        self.assertEqual(config["accounts"][0]["games"][1], 440)
        self.assertEqual(config["accounts"][0]["games"][2], 570)

if __name__ == '__main__':
    unittest.main()
