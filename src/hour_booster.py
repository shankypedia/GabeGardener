import os
import time
import json
import jwt
import getpass
import pyotp
from steam.client import SteamClient
from steam.enums import EPersonaState
from config.global_config import clock

class SteamBot:
    def __init__(self, config):
        self.client = SteamClient()
        
        # Create necessary directories
        self.accounts_path = './accounts_data'
        self.login_keys_path = './login_keys'
        if not os.path.exists(self.login_keys_path):
            os.makedirs(self.login_keys_path)
        
        # Set bot properties from config
        self.username = config['username']
        self.password = config['password']
        self.shared_secret = config['shared_secret']
        self.games = config['games_and_status']
        self.custom_status = config['enable_status']
        self.auto_message = config['reply_message']
        self.receive_messages = config['receive_messages']
        self.save_messages = config['save_messages']
        self.message_received = {}
        
        # Login key file path
        self.login_key_path = f"{self.login_keys_path}/{self.username}.txt"
        
        # Create messages directory if needed
        if self.save_messages:
            try:
                if not os.path.exists("messages"):
                    os.makedirs("messages")
                if not os.path.exists(f"messages/{self.username}"):
                    os.makedirs(f"messages/{self.username}")
            except Exception as e:
                print(f"[{self.username}] Error creating message directories: {e}")
        
        # Register event handlers
        self.client.on('logged_on', self._on_logged_on)
        self.client.on('error', self._on_error)
        self.client.on('login_key', self._on_login_key)
        self.client.on('chat_message', self._on_chat_message)
    
    def _on_logged_on(self):
        print(f"[{self.username}] Logged into Steam as {self.client.user.steam_id}\n")
        
        if self.custom_status:
            self.client.set_persona_state(EPersonaState.Online)
        else:
            self.client.set_persona_state(EPersonaState.Invisible)
        
        # Set games being played
        self.client.games_played(self.games)
    
    def _on_error(self, err):
        print(f"[{self.username}] {err}\n")
        
        # If invalid password, remove login key
        if "Invalid Password" in str(err):
            if os.path.exists(self.login_key_path):
                os.remove(self.login_key_path)
        
        # Retry login after delay
        print(f"[{self.username}] Retrying login in 30 minutes...")
        time.sleep(30 * 60)
        self.do_login()
    
    def _on_login_key(self, key):
        with open(self.login_key_path, 'w') as f:
            f.write(key)
        print(f"[{self.username}] Login key saved!\n")
    
    def _on_chat_message(self, user, message_text):
        steam_id = user.steam_id
        
        if self.receive_messages:
            print(f"[{self.username}] Message from {steam_id}: {message_text}\n")
        
        if self.save_messages:
            message_file = f"messages/{self.username}/{steam_id}.log"
            try:
                with open(message_file, 'a') as f:
                    f.write(f"{message_text}\n")
            except Exception as e:
                print(f"[{self.username}] Error saving message from {steam_id}: {e}\n")
        
        # Send auto-reply if configured and first message
        if steam_id not in self.message_received and self.auto_message:
            self.client.chat_send_message(steam_id, self.auto_message)
            self.message_received[steam_id] = True
    
    def do_login(self):
        if os.path.exists(self.login_key_path):
            try:
                with open(self.login_key_path, 'r') as f:
                    login_key = f.read().strip()
                
                # Validate login key format
                try:
                    jwt.decode(login_key, options={"verify_signature": False})
                except:
                    os.remove(self.login_key_path)
                    self.do_login()
                    return
                
                # Login with key
                self.client.login(username=self.username, login_key=login_key, auth_code_callback=self._auth_code_callback)
            except Exception as e:
                print(f"[{self.username}] Error using login key: {e}")
                if os.path.exists(self.login_key_path):
                    os.remove(self.login_key_path)
                self.do_login()
        else:
            # Login with password
            self.client.login(username=self.username, password=self.password, auth_code_callback=self._auth_code_callback)
    
    def _auth_code_callback(self):
        if self.shared_secret:
            # Generate code from shared secret
            totp = pyotp.TOTP(self.shared_secret)
            auth_code = totp.now()
            print(f"[{self.username}] Generated Auth Code: {auth_code}\n")
            return auth_code
        else:
            # Ask for manual code input
            auth_code = input(f"[{self.username}] Steam Guard Code: ")
            return auth_code

def build_bot(config):
    """Factory function to create and return a configured SteamBot instance"""
    return SteamBot(config)
