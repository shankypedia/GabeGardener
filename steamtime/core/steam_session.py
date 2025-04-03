"""
Steam session module for GabeGardener.

This module provides the SteamSession class for interacting with Steam.
"""
import time
import logging
import threading
from typing import List, Dict, Any, Optional, Union, Callable

import steam.client
from steam.client import SteamClient
from steam.enums import EResult, EPersonaState
from steam.enums.emsg import EMsg

from steamtime.models.account import Account
from steamtime.utils.file_manager import save_login_key, load_login_key, save_message
from steamtime.utils.stats import update_account_stats, update_game_stats

logger = logging.getLogger("gabegardener")

class SteamSession:
    """
    Steam session class for managing a Steam account session.
    
    This class handles login, game playing, and message handling.
    """
    
    def __init__(self, account: Account):
        """
        Initialize a new Steam session.
        
        Args:
            account (Account): The account to use for this session
        """
        self.account = account
        self.client = SteamClient()
        self.logged_on = False
        self.running = False
        self.thread = None
        self.last_message_time = {}  # Track last message time per user
        
        # Set up callbacks
        self.client.on('logged_on', self._handle_logged_on)
        self.client.on('disconnected', self._handle_disconnected)
        self.client.on('reconnect', self._handle_reconnect)
        self.client.on('error', self._handle_error)
        self.client.on('chat_message', self._handle_chat_message)
        self.client.on(EMsg.ClientPersonaState, self._handle_persona_state)
        
        # Load login key if available
        self.account.login_key = load_login_key(self.account.username)
    
    def start(self):
        """Start the Steam session in a separate thread."""
        if self.thread and self.thread.is_alive():
            logger.warning(f"Session for {self.account.username} is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_session)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"Started session for {self.account.username}")
    
    def stop(self):
        """Stop the Steam session."""
        self.running = False
        if self.logged_on:
            try:
                self.client.logout()
            except Exception as e:
                logger.error(f"Error logging out {self.account.username}: {e}")
        
        try:
            self.client.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting {self.account.username}: {e}")
        
        logger.info(f"Stopped session for {self.account.username}")
    
    def _run_session(self):
        """Run the Steam session."""
        try:
            # Connect to Steam
            self.client.connect()
            
            # Main loop
            while self.running:
                # Try to log in if not logged on
                if not self.logged_on:
                    self._login()
                
                # Sleep to avoid high CPU usage
                time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error in session for {self.account.username}: {e}")
        finally:
            # Ensure we're disconnected
            try:
                self.client.disconnect()
            except:
                pass
    
    def _login(self):
        """Log in to Steam."""
        try:
            logger.info(f"Logging in {self.account.username}...")
            self.account.status = "logging_in"
            
            # Prepare login details
            login_details = {
                'username': self.account.username,
                'password': self.account.password,
            }
            
            # Add login key if available
            if self.account.login_key:
                login_details['login_key'] = self.account.login_key
            
            # Add two-factor code if available
            if self.account.shared_secret:
                import pyotp
                totp = pyotp.TOTP(self.account.shared_secret)
                login_details['two_factor_code'] = totp.now()
            
            # Attempt login
            result = self.client.login(**login_details)
            
            if result == EResult.OK:
                logger.info(f"Logged in {self.account.username} successfully")
                self.logged_on = True
                self.account.status = "online"
                
                # Update stats
                update_account_stats(self.account.username, "logins")
                
                # Set persona state
                self._set_persona_state()
                
                # Start playing games
                self._play_games()
            else:
                logger.error(f"Login failed for {self.account.username}: {result.name}")
                self.account.status = "login_failed"
                
                # Clear login key if login failed
                self.account.login_key = None
                
                # Wait before retrying
                time.sleep(30)
        
        except Exception as e:
            logger.error(f"Error logging in {self.account.username}: {e}")
            self.account.status = "login_error"
            time.sleep(30)
    
    def _set_persona_state(self):
        """Set the persona state (online/invisible)."""
        try:
            state = EPersonaState.Online if self.account.visible else EPersonaState.Invisible
            self.client.change_status(persona_state=state)
            logger.debug(f"Set {self.account.username} to {state.name}")
        except Exception as e:
            logger.error(f"Error setting persona state for {self.account.username}: {e}")
    
    def _play_games(self):
        """Start playing games."""
        try:
            # Get game IDs
            game_ids = []
            for game in self.account.games:
                if isinstance(game, int) or (isinstance(game, str) and game.isdigit()):
                    game_ids.append(int(game))
            
            # Start playing games
            if game_ids:
                self.client.games_played(game_ids)
                self.account.current_games = game_ids
                logger.info(f"{self.account.username} is now playing {len(game_ids)} games")
                
                # Update game stats
                for game_id in game_ids:
                    update_game_stats(self.account.username, game_id)
        except Exception as e:
            logger.error(f"Error playing games for {self.account.username}: {e}")
    
    def _handle_logged_on(self):
        """Handle logged on event."""
        logger.debug(f"{self.account.username} logged on")
        self.logged_on = True
        self.account.status = "online"
        
        # Save login key if provided
        if self.client.login_key:
            self.account.login_key = self.client.login_key
            save_login_key(self.account.username, self.client.login_key)
    
    def _handle_disconnected(self):
        """Handle disconnected event."""
        logger.info(f"{self.account.username} disconnected from Steam")
        self.logged_on = False
        self.account.status = "offline"
        
        # Reconnect if still running
        if self.running:
            logger.info(f"Reconnecting {self.account.username}...")
            time.sleep(5)  # Wait before reconnecting
            self.client.connect()
    
    def _handle_reconnect(self, delay):
        """
        Handle reconnect event.
        
        Args:
            delay (int): Delay before reconnecting
        """
        logger.info(f"{self.account.username} reconnecting in {delay} seconds")
        self.logged_on = False
        self.account.status = "reconnecting"
    
    def _handle_error(self, result):
        """
        Handle error event.
        
        Args:
            result (EResult): Error result
        """
        logger.error(f"Error for {self.account.username}: {result.name}")
        
        # Handle specific errors
        if result == EResult.InvalidPassword:
            logger.error(f"Invalid password for {self.account.username}")
            self.account.status = "invalid_password"
            self.running = False  # Stop trying to reconnect
        elif result == EResult.RateLimitExceeded:
            logger.error(f"Rate limit exceeded for {self.account.username}")
            self.account.status = "rate_limited"
            time.sleep(60)  # Wait longer before retrying
    
    def _handle_chat_message(self, user, message_text, **kwargs):
        """
        Handle chat message event.
        
        Args:
            user (SteamID): Steam ID of the sender
            message_text (str): Message content
            **kwargs: Additional arguments
        """
        if not self.account.receive_messages:
            return
        
        sender_id = user.as_64
        logger.info(f"{self.account.username} received message from {sender_id}: {message_text}")
        
        # Update stats
        update_account_stats(self.account.username, "messages_received")
        
        # Save message if enabled
        if self.account.save_messages:
            save_message(
                self.account.username,
                str(sender_id),
                message_text,
                int(time.time())
            )
        
        # Send auto-reply if enabled
        if self.account.auto_reply:
            # Check if we've sent a message to this user recently
            current_time = time.time()
            last_time = self.last_message_time.get(sender_id, 0)
            
            # Only send auto-reply once per hour per user
            if current_time - last_time > 3600:
                try:
                    self.client.send_user_message(user, self.account.auto_reply)
                    self.last_message_time[sender_id] = current_time
                    logger.debug(f"Sent auto-reply to {sender_id}")
                    
                    # Update stats
                    update_account_stats(self.account.username, "messages_sent")
                except Exception as e:
                    logger.error(f"Error sending auto-reply to {sender_id}: {e}")
    
    def _handle_persona_state(self, msg):
        """
        Handle persona state event.
        
        Args:
            msg: Persona state message
        """
        # This is just for debugging
        pass
    
    def rotate_games(self):
        """Rotate the games being played."""
        if not self.logged_on or not self.account.game_rotation:
            return
        
        try:
            # Get game IDs
            game_ids = []
            for game in self.account.games:
                if isinstance(game, int) or (isinstance(game, str) and game.isdigit()):
                    game_ids.append(int(game))
            
            if len(game_ids) <= 1:
                return  # No need to rotate with 0 or 1 games
            
            # Rotate games
            rotated_games = game_ids[1:] + [game_ids[0]]
            
            # Update account games
            new_games = []
            game_index = 0
            for game in self.account.games:
                if isinstance(game, int) or (isinstance(game, str) and game.isdigit()):
                    new_games.append(rotated_games[game_index])
                    game_index += 1
                else:
                    new_games.append(game)
            
            self.account.games = new_games
            
            # Start playing rotated games
            self.client.games_played(rotated_games)
            self.account.current_games = rotated_games
            self.account.last_rotation = int(time.time())
            
            logger.info(f"Rotated games for {self.account.username}")
            
            # Update game stats
            for game_id in rotated_games:
                update_game_stats(self.account.username, game_id)
        
        except Exception as e:
            logger.error(f"Error rotating games for {self.account.username}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the session.
        
        Returns:
            Dict[str, Any]: Session status
        """
        return {
            "username": self.account.username,
            "status": self.account.status,
            "visible": self.account.visible,
            "games": self.account.current_games,
            "game_count": len(self.account.current_games),
            "auto_reply": bool(self.account.auto_reply),
            "game_rotation": self.account.game_rotation,
            "last_rotation": self.account.last_rotation
        }
