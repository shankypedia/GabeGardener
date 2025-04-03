"""
Cryptography utilities for GabeGardener.

This module provides functions for encrypting and decrypting sensitive data
such as passwords in the configuration file.
"""
import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Get machine-specific key
def _get_machine_key():
    """
    Generate a machine-specific key for encryption.
    
    This creates a key based on hardware and OS information to ensure
    encrypted data can only be decrypted on the same machine.
    """
    # Get machine-specific information
    machine_info = ""
    
    # Add hostname
    try:
        machine_info += os.uname().nodename
    except:
        try:
            import socket
            machine_info += socket.gethostname()
        except:
            pass
    
    # Add user information
    try:
        machine_info += os.getlogin()
    except:
        try:
            machine_info += os.environ.get('USERNAME', '')
        except:
            pass
    
    # Add OS information
    try:
        machine_info += os.uname().sysname + os.uname().release
    except:
        try:
            import platform
            machine_info += platform.system() + platform.release()
        except:
            pass
    
    # Hash the machine info to create a consistent key
    if not machine_info:
        machine_info = "gabegardener-default-key"
    
    return hashlib.sha256(machine_info.encode()).digest()

def _get_encryption_key():
    """
    Get the encryption key for Fernet.
    
    Returns:
        bytes: The encryption key
    """
    # Use machine-specific information as salt
    salt = _get_machine_key()[:16]
    
    # Use a fixed password combined with machine-specific info
    password = b"gabegardener-encryption-key" + _get_machine_key()
    
    # Generate a key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def encrypt_password(password):
    """
    Encrypt a password.
    
    Args:
        password (str): The password to encrypt
        
    Returns:
        str: The encrypted password as a base64 string
    """
    key = _get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(password.encode())
    return base64.urlsafe_b64encode(encrypted).decode()

def decrypt_password(encrypted_password):
    """
    Decrypt an encrypted password.
    
    Args:
        encrypted_password (str): The encrypted password as a base64 string
        
    Returns:
        str: The decrypted password
    """
    key = _get_encryption_key()
    f = Fernet(key)
    encrypted = base64.urlsafe_b64decode(encrypted_password)
    return f.decrypt(encrypted).decode()
