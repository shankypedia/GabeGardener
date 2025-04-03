"""
Update checker for GabeGardener.

This module provides functions for checking for updates.
"""
import json
import logging
import urllib.request
from datetime import datetime, timedelta

logger = logging.getLogger("gabegardener")

# Current version
VERSION = "1.0.0"

# GitHub repository information
REPO_OWNER = "shankypedia"
REPO_NAME = "GabeGardenerREPO_NAME = "GabeGardener"
REPO_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

# Last check file
def get_last_check_file():
    """
    Get the path to the last update check file.
    
    Returns:
        str: Path to the last update check file
    """
    from steamtime.utils.file_manager import get_config_dir
    import os
    return os.path.join(get_config_dir(), "last_update_check.json")

def should_check_for_updates():
    """
    Determine if we should check for updates.
    
    Returns:
        bool: True if we should check for updates
    """
    last_check_file = get_last_check_file()
    
    try:
        import os
        if not os.path.exists(last_check_file):
            return True
        
        with open(last_check_file, 'r') as f:
            data = json.load(f)
        
        last_check = datetime.fromisoformat(data.get("last_check"))
        check_interval = timedelta(days=1)  # Check once per day
        
        return datetime.now() - last_check > check_interval
    except Exception as e:
        logger.debug(f"Error checking update status: {e}")
        return True

def save_last_check():
    """Save the last update check time."""
    last_check_file = get_last_check_file()
    
    try:
        with open(last_check_file, 'w') as f:
            json.dump({
                "last_check": datetime.now().isoformat(),
                "version": VERSION
            }, f)
    except Exception as e:
        logger.debug(f"Error saving update check: {e}")

def check_for_updates():
    """
    Check for updates to GabeGardener.
    
    Returns:
        tuple: (bool, str) - (update_available, latest_version)
    """
    if not should_check_for_updates():
        return False, VERSION
    
    try:
        # Set a timeout for the request
        req = urllib.request.Request(
            REPO_API_URL,
            headers={"User-Agent": f"GabeGardener/{VERSION}"}
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            
            latest_version = data.get("tag_name", "").lstrip("v")
            
            # Save last check
            save_last_check()
            
            # Compare versions
            if latest_version and latest_version != VERSION:
                logger.info(f"New version available: {latest_version} (current: {VERSION})")
                return True, latest_version
            
            return False, VERSION
    except Exception as e:
        logger.debug(f"Error checking for updates: {e}")
        return False, VERSION
