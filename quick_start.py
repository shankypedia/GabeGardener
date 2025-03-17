#!/usr/bin/env python3
"""
GabeGardener Quick Start

This script helps users quickly set up GabeGardener with a guided
configuration process.
"""
import os
import json
import getpass
import sys

def create_config():
    """Create a configuration file with user input."""
    print("Welcome to GabeGardener Quick Start!")
    print("Let's set up your configuration.")
    
    # Create config directory
    config_dir = os.path.join(os.path.expanduser("~"), ".gabegardener")
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, "config.json")
    
    # Check if config already exists
    if os.path.exists(config_path):
        overwrite = input("Configuration already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Setup cancelled. Using existing configuration.")
            return
    
    # Get user input
    accounts = []
    while True:
        print("\nSteam Account Setup:")
        username = input("Steam Username: ")
        password = getpass.getpass("Steam Password: ")
        shared_secret = getpass.getpass("Steam Shared Secret (optional, press Enter to skip): ")
        
        games = ["GabeGardener", 730, 440, 570]  # Default games
        custom_games = input("Custom games (comma-separated IDs, or press Enter for defaults): ")
        if custom_games:
            games = ["GabeGardener"]  # Always include app name
            for game in custom_games.split(','):
                game = game.strip()
                if game.isdigit():
                    games.append(int(game))
                else:
                    games.append(game)
        
        accounts.append({
            "username": username,
            "password": password,
            "shared_secret": shared_secret,
            "visible": True,
            "games": games,
            "auto_reply": "I am currently AFK. This is an automated message.",
            "receive_messages": True,
            "save_messages": True
        })
        
        another = input("Add another account? (y/n): ").lower()
        if another != 'y':
            break
    
    # Dashboard settings
    dashboard_enabled = input("\nEnable web dashboard? (y/n): ").lower() == 'y'
    dashboard_port = 5000
    if dashboard_enabled:
        port_input = input(f"Dashboard port (default: {dashboard_port}): ")
        if port_input and port_input.isdigit():
            dashboard_port = int(port_input)
    
    # Create config
    config = {
        "show_timer": True,
        "enable_game_rotation": False,
        "rotation_interval": 3600,
        "language": "en",
        "auto_update_check": True,
        "dashboard_port": dashboard_port,
        "dashboard_enabled": dashboard_enabled,
        "accounts": accounts
    }
    
    # Save config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Set permissions
    os.chmod(config_path, 0o600)
    
    print(f"\nConfiguration saved to {config_path}")
    print("To start GabeGardener, run: python main.py")

if __name__ == "__main__":
    try:
        create_config()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        sys.exit(1)
