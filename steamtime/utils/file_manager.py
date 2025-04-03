"""
File management utilities for GabeGardener.

This module provides functions for managing files and directories.
"""
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger("gabegardener")

def get_config_dir():
    """
    Get the configuration directory.
    
    Returns:
        str: Path to the configuration directory
    """
    config_dir = os.environ.get("GABEGARDENER_CONFIG_DIR", 
                               os.path.join(os.path.expanduser("~"), ".gabegardener"))
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def get_login_keys_dir():
    """
    Get the login keys directory.
    
    Returns:
        str: Path to the login keys directory
    """
    login_keys_dir = os.path.join(get_config_dir(), "login_keys")
    os.makedirs(login_keys_dir, exist_ok=True)
    return login_keys_dir

def get_logs_dir():
    """
    Get the logs directory.
    
    Returns:
        str: Path to the logs directory
    """
    logs_dir = os.environ.get("GABEGARDENER_LOG_DIR", 
                             os.path.join(get_config_dir(), "logs"))
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def get_messages_dir():
    """
    Get the messages directory.
    
    Returns:
        str: Path to the messages directory
    """
    messages_dir = os.path.join(get_config_dir(), "messages")
    os.makedirs(messages_dir, exist_ok=True)
    return messages_dir

def save_login_key(username, login_key):
    """
    Save a login key for a Steam account.
    
    Args:
        username (str): Steam username
        login_key (str): Login key to save
    """
    login_keys_dir = get_login_keys_dir()
    login_key_file = os.path.join(login_keys_dir, f"{username}.key")
    
    try:
        with open(login_key_file, 'w') as f:
            f.write(login_key)
        
        # Set secure permissions
        os.chmod(login_key_file, 0o600)
        logger.debug(f"Saved login key for {username}")
    except Exception as e:
        logger.error(f"Error saving login key for {username}: {e}")

def load_login_key(username):
    """
    Load a login key for a Steam account.
    
    Args:
        username (str): Steam username
        
    Returns:
        str: Login key or None if not found
    """
    login_keys_dir = get_login_keys_dir()
    login_key_file = os.path.join(login_keys_dir, f"{username}.key")
    
    if os.path.exists(login_key_file):
        try:
            with open(login_key_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error loading login key for {username}: {e}")
    
    return None

def save_message(username, sender, message, timestamp):
    """
    Save a received message.
    
    Args:
        username (str): Steam username (receiver)
        sender (str): Sender's Steam ID
        message (str): Message content
        timestamp (int): Message timestamp
    """
    messages_dir = get_messages_dir()
    user_dir = os.path.join(messages_dir, username)
    os.makedirs(user_dir, exist_ok=True)
    
    # Create a filename with timestamp
    from datetime import datetime
    date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    messages_file = os.path.join(user_dir, f"{date_str}.json")
    
    # Load existing messages
    messages = []
    if os.path.exists(messages_file):
        try:
            with open(messages_file, 'r') as f:
                messages = json.load(f)
        except Exception as e:
            logger.error(f"Error loading messages file: {e}")
    
    # Add new message
    messages.append({
        "sender": sender,
        "message": message,
        "timestamp": timestamp
    })
    
    # Save messages
    try:
        with open(messages_file, 'w') as f:
            json.dump(messages, f, indent=2)
        logger.debug(f"Saved message from {sender} to {username}")
    except Exception as e:
        logger.error(f"Error saving message: {e}")
