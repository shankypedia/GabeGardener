"""
Configuration settings module for GabeGardener.

This module handles loading, saving, and managing configuration settings
from various sources with the following priority:
1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default values
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Union, Optional

from steamtime.utils.crypto import encrypt_password, decrypt_password
from steamtime.config.default_config import DEFAULT_CONFIG

# Logger
logger = logging.getLogger("gabegardener")

# Configuration paths
CONFIG_DIR = os.environ.get("GABEGARDENER_CONFIG_DIR", 
                           os.path.join(os.path.expanduser("~"), ".gabegardener"))
CONFIG_FILE = os.environ.get("GABEGARDENER_CONFIG", 
                            os.path.join(CONFIG_DIR, "config.json"))

def ensure_config_dir():
    """Ensure the configuration directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Create login keys directory
    login_keys_dir = os.path.join(CONFIG_DIR, "login_keys")
    os.makedirs(login_keys_dir, exist_ok=True)
    
    # Set secure permissions
    try:
        os.chmod(CONFIG_DIR, 0o700)
        os.chmod(login_keys_dir, 0o700)
    except Exception as e:
        logger.warning(f"Could not set secure permissions: {e}")

def load_config() -> Dict[str, Any]:
    """
    Load configuration from file or environment variables.
    
    Returns:
        Dict[str, Any]: The configuration dictionary
    """
    ensure_config_dir()
    config = DEFAULT_CONFIG.copy()
    
    # Try to load from config file
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
                logger.info(f"Loaded configuration from {CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    # Check for environment variable configuration
    env_config_json = os.environ.get("GABEGARDENER_CONFIG_JSON")
    if env_config_json:
        try:
            env_config = json.loads(env_config_json)
            config.update(env_config)
            logger.info("Loaded configuration from environment variable")
        except Exception as e:
            logger.error(f"Error parsing environment config: {e}")
    
    # Check for individual environment variables
    if "GABEGARDENER_DASHBOARD" in os.environ:
        config["dashboard_enabled"] = os.environ["GABEGARDENER_DASHBOARD"].lower() == "true"
    
    if "GABEGARDENER_DASHBOARD_PORT" in os.environ:
        try:
            config["dashboard_port"] = int(os.environ["GABEGARDENER_DASHBOARD_PORT"])
        except ValueError:
            logger.error("Invalid dashboard port in environment variable")
    
    # Process accounts
    for account in config.get("accounts", []):
        # Decrypt passwords if they're encrypted
        if account.get("password") and account.get("password").startswith("enc:"):
            try:
                account["password"] = decrypt_password(account["password"][4:])
            except Exception as e:
                logger.error(f"Error decrypting password for {account.get('username')}: {e}")
    
    return config

def save_config(config: Dict[str, Any]):
    """
    Save configuration to file.
    
    Args:
        config (Dict[str, Any]): The configuration to save
    """
    ensure_config_dir()
    
    # Create a copy to avoid modifying the original
    config_to_save = config.copy()
    
    # Encrypt passwords before saving
    for account in config_to_save.get("accounts", []):
        if account.get("password") and not account["password"].startswith("enc:"):
            account["password"] = f"enc:{encrypt_password(account['password'])}"
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_to_save, f, indent=2)
        
        # Set secure permissions
        os.chmod(CONFIG_FILE, 0o600)
        logger.info(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Error saving config file: {e}")

def add_account(username: str, password: str, games: List[Union[str, int]], 
                shared_secret: Optional[str] = None):
    """
    Add a new account to the configuration.
    
    Args:
        username (str): Steam username
        password (str): Steam password
        games (List[Union[str, int]]): List of game IDs or names
        shared_secret (Optional[str]): Shared secret for 2FA
    """
    config = load_config()
    
    # Convert string game IDs to integers where possible
    processed_games = []
    for game in games:
        if isinstance(game, str) and game.isdigit():
            processed_games.append(int(game))
        else:
            processed_games.append(game)
    
    # Create new account
    new_account = {
        "username": username,
        "password": password,
        "shared_secret": shared_secret or "",
        "visible": True,
        "games": processed_games,
        "auto_reply": "I am currently AFK. This is an automated message.",
        "receive_messages": True,
        "save_messages": True
    }
    
    # Check if account already exists
    for i, account in enumerate(config.get("accounts", [])):
        if account.get("username") == username:
            # Update existing account
            config["accounts"][i] = new_account
            save_config(config)
            return
    
    # Add new account
    if "accounts" not in config:
        config["accounts"] = []
    config["accounts"].append(new_account)
    save_config(config)

def remove_account(username: str):
    """
    Remove an account from the configuration.
    
    Args:
        username (str): Steam username to remove
    """
    config = load_config()
    
    if "accounts" in config:
        config["accounts"] = [acc for acc in config["accounts"] 
                             if acc.get("username") != username]
        save_config(config)
