"""
Logging utilities for GabeGardener.

This module provides functions for setting up and configuring logging.
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger():
    """
    Set up the logger for GabeGardener.
    
    This configures both console and file logging.
    """
    # Create logger
    logger = logging.getLogger("gabegardener")
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Create logs directory
    log_dir = os.environ.get("GABEGARDENER_LOG_DIR", 
                            os.path.join(os.path.expanduser("~"), ".gabegardener", "logs"))
    os.makedirs(log_dir, exist_ok=True)
    
    # Create file handler
    log_file = os.path.join(log_dir, "gabegardener.log")
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Add file handler to logger
    logger.addHandler(file_handler)
    
    return logger
