"""
Session manager module for GabeGardener.

This module provides the SessionManager class for managing multiple Steam sessions.
"""
import time
import logging
import threading
from typing import Dict, List, Any, Optional

from steamtime.models.account import Account
from steamtime.core.steam_session import SteamSession
from steamtime.utils.stats import update_uptime

logger = logging.getLogger("gabegardener")

class SessionManager:
    """
    Session manager class for managing multiple Steam sessions.
    
    This class handles starting, stopping, and monitoring multiple Steam sessions.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize a new session manager.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
        self.config = config
        self.sessions: Dict[str, SteamSession] = {}
        self.accounts: Dict[str, Account] = {}
        self.running = False
        self.monitor_thread = None
        
        # Load accounts from config
        self._load_accounts()
    
    def _load_accounts(self):
        """Load accounts from configuration."""
        for account_data in self.config.get("accounts", []):
            try:
                account = Account.from_dict(account_data)
                self.accounts[account.username] = account
            except Exception as e:
                logger.error(f"Error loading account: {e}")
    
    def start_all_sessions(self):
        """Start sessions for all accounts."""
        if self.running:
            logger.warning("Session manager is already running")
            return
        
        self.running = True
        
        # Start sessions for each account
        for username, account in self.accounts.items():
            try:
                session = SteamSession(account)
                self.sessions[username] = session
                session.start()
            except Exception as e:
                logger.error(f"Error starting session for {username}: {e}")
        
        # Start monitor thread
        self.monitor_thread = threading.Thread(target=self._monitor_sessions)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info(f"Started {len(self.sessions)} sessions")
    
    def stop_all_sessions(self):
        """Stop all running sessions."""
        self.running = False
        
        # Stop each session
        for username, session in self.sessions.items():
            try:
                session.stop()
            except Exception as e:
                logger.error(f"Error stopping session for {username}: {e}")
        
        # Clear sessions
        self.sessions = {}
        
        logger.info("Stopped all sessions")
    
    def _monitor_sessions(self):
        """Monitor sessions and handle game rotation."""
        rotation_interval = self.config.get("rotation_interval", 3600)  # Default: 1 hour
        stats_update_interval = 300  # Update stats every 5 minutes
        last_stats_update = time.time()
        
        while self.running:
            current_time = time.time()
            
            # Check each session
            for username, session in list(self.sessions.items()):
                # Check if session thread is alive
                if not session.thread or not session.thread.is_alive():
                    logger.warning(f"Session for {username} died, restarting")
                    try:
                        # Recreate and restart session
                        new_session = SteamSession(self.accounts[username])
                        self.sessions[username] = new_session
                        new_session.start()
                    except Exception as e:
                        logger.error(f"Error restarting session for {username}: {e}")
                
                # Handle game rotation
                if session.account.game_rotation:
                    account_interval = session.account.rotation_interval or rotation_interval
                    if current_time - session.account.last_rotation >= account_interval:
                        try:
                            session.rotate_games()
                        except Exception as e:
                            logger.error(f"Error rotating games for {username}: {e}")
            
            # Update statistics periodically
            if current_time - last_stats_update >= stats_update_interval:
                try:
                    update_uptime()
                    last_stats_update = current_time
                except Exception as e:
                    logger.error(f"Error updating statistics: {e}")
            
            # Sleep to avoid high CPU usage
            time.sleep(10)
    
    def get_session_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all sessions.
        
        Returns:
            List[Dict[str, Any]]: List of session status dictionaries
        """
        status_list = []
        
        for username, session in self.sessions.items():
            try:
                status = session.get_status()
                status_list.append(status)
            except Exception as e:
                logger.error(f"Error getting status for {username}: {e}")
                status_list.append({
                    "username": username,
                    "status": "error",
                    "error": str(e)
                })
        
        return status_list
    
    def print_status(self):
        """Print status of all sessions to console."""
        from tabulate import tabulate
        
        status_list = self.get_session_status()
        
        if not status_list:
            print("No active sessions")
            return
        
        # Prepare table data
        table_data = []
        for status in status_list:
            table_data.append([
                status["username"],
                status["status"],
                "Yes" if status["visible"] else "No",
                status["game_count"],
                "Yes" if status["auto_reply"] else "No",
                "Yes" if status["game_rotation"] else "No"
            ])
        
        # Print table
        print("\nGabeGardener Session Status")
        print("==========================")
        print(tabulate(
            table_data,
            headers=["Username", "Status", "Visible", "Games", "Auto-Reply", "Rotation"],
            tablefmt="grid"
        ))
    
    def wait_for_sessions(self):
        """Wait for all sessions to complete (blocks until interrupted)."""
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all_sessions()
