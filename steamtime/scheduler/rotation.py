"""
Game rotation scheduler for GabeGardener.

This module provides functionality for rotating games on a schedule.
"""
import time
import logging
import threading
from typing import Dict, Any

logger = logging.getLogger("gabegardener")

class GameRotationScheduler:
    """
    Game rotation scheduler class.
    
    This class handles scheduling game rotations for accounts.
    """
    
    def __init__(self, session_manager):
        """
        Initialize a new game rotation scheduler.```
        Args:
            session_manager: Session manager instance
        """
        self.session_manager = session_manager
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the game rotation scheduler."""
        if self.thread and self.thread.is_alive():
            logger.warning("Game rotation scheduler is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Started game rotation scheduler")
    
    def stop(self):
        """Stop the game rotation scheduler."""
        self.running = False
        logger.info("Stopped game rotation scheduler")
    
    def _run_scheduler(self):
        """Run the game rotation scheduler."""
        try:
            # Get global rotation interval
            config = self.session_manager.config
            global_rotation_interval = config.get("rotation_interval", 3600)  # Default: 1 hour
            
            while self.running:
                current_time = time.time()
                
                # Check each session for rotation
                for username, session in self.session_manager.sessions.items():
                    if not session.account.game_rotation:
                        continue
                    
                    # Get account-specific interval or use global
                    interval = session.account.rotation_interval or global_rotation_interval
                    
                    # Check if it's time to rotate
                    if current_time - session.account.last_rotation >= interval:
                        try:
                            session.rotate_games()
                            logger.info(f"Rotated games for {username}")
                        except Exception as e:
                            logger.error(f"Error rotating games for {username}: {e}")
                
                # Sleep to avoid high CPU usage (check every minute)
                time.sleep(60)
        
        except Exception as e:
            logger.error(f"Error in game rotation scheduler: {e}")
