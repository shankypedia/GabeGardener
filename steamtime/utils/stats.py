"""
Statistics utilities for GabeGardener.

This module provides functions for tracking and reporting statistics.
"""
import os
import json
import time
import logging
from datetime import datetime, timedelta
from tabulate import tabulate

logger = logging.getLogger("gabegardener")

# Stats file path
def get_stats_file():
    """
    Get the path to the statistics file.
    
    Returns:
        str: Path to the statistics file
    """
    from steamtime.utils.file_manager import get_config_dir
    stats_dir = os.path.join(get_config_dir(), "stats")
    os.makedirs(stats_dir, exist_ok=True)
    return os.path.join(stats_dir, "stats.json")

def load_stats():
    """
    Load statistics from file.
    
    Returns:
        dict: Statistics data
    """
    stats_file = get_stats_file()
    
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading stats file: {e}")
    
    # Return default stats structure
    return {
        "accounts": {},
        "global": {
            "start_time": int(time.time()),
            "total_uptime": 0,
            "total_messages": 0,
            "total_logins": 0,
            "last_update": int(time.time())
        }
    }

def save_stats(stats):
    """
    Save statistics to file.
    
    Args:
        stats (dict): Statistics data to save
    """
    stats_file = get_stats_file()
    
    # Update last update time
    stats["global"]["last_update"] = int(time.time())
    
    try:
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving stats file: {e}")

def update_account_stats(username, key, value=1, increment=True):
    """
    Update statistics for an account.
    
    Args:
        username (str): Steam username
        key (str): Statistic key to update
        value (any): Value to set or increment by
        increment (bool): Whether to increment or set the value
    """
    stats = load_stats()
    
    # Ensure account exists in stats
    if username not in stats["accounts"]:
        stats["accounts"][username] = {
            "start_time": int(time.time()),
            "uptime": 0,
            "messages_received": 0,
            "messages_sent": 0,
            "logins": 0,
            "games_played": {}
        }
    
    # Update the statistic
    if increment and key in stats["accounts"][username]:
        stats["accounts"][username][key] += value
    else:
        stats["accounts"][username][key] = value
    
    # Update global stats
    if key == "messages_received" or key == "messages_sent":
        stats["global"]["total_messages"] += value
    elif key == "logins":
        stats["global"]["total_logins"] += value
    
    save_stats(stats)

def update_game_stats(username, game_id):
    """
    Update game play statistics for an account.
    
    Args:
        username (str): Steam username
        game_id (int): Game ID being played
    """
    stats = load_stats()
    
    # Ensure account exists in stats
    if username not in stats["accounts"]:
        update_account_stats(username, "uptime", 0)
    
    # Convert game_id to string for JSON compatibility
    game_id = str(game_id)
    
    # Update game stats
    if "games_played" not in stats["accounts"][username]:
        stats["accounts"][username]["games_played"] = {}
    
    if game_id not in stats["accounts"][username]["games_played"]:
        stats["accounts"][username]["games_played"][game_id] = 0
    
    stats["accounts"][username]["games_played"][game_id] += 1
    
    save_stats(stats)

def update_uptime():
    """Update uptime statistics for all accounts."""
    stats = load_stats()
    
    # Calculate time since last update
    last_update = stats["global"]["last_update"]
    current_time = int(time.time())
    time_diff = current_time - last_update
    
    # Update global uptime
    stats["global"]["total_uptime"] += time_diff
    
    # Update account uptimes
    for username in stats["accounts"]:
        stats["accounts"][username]["uptime"] += time_diff
    
    save_stats(stats)

def generate_stats_report(output_file=None):
    """
    Generate a statistics report.
    
    Args:
        output_file (str, optional): File to write the report to
    
    Returns:
        str: Statistics report
    """
    stats = load_stats()
    
    # Update uptime before generating report
    update_uptime()
    
    # Format start time
    start_time = datetime.fromtimestamp(stats["global"]["start_time"])
    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Format uptime
    uptime = timedelta(seconds=stats["global"]["total_uptime"])
    uptime_str = str(uptime).split('.')[0]  # Remove microseconds
    
    # Create report
    report = [
        "GabeGardener Statistics Report",
        "===========================",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Started: {start_time_str}",
        f"Total Uptime: {uptime_str}",
        f"Total Messages: {stats['global']['total_messages']}",
        f"Total Logins: {stats['global']['total_logins']}",
        "",
        "Account Statistics",
        "-----------------"
    ]
    
    # Create account table
    account_data = []
    for username, account_stats in stats["accounts"].items():
        account_uptime = timedelta(seconds=account_stats["uptime"])
        account_uptime_str = str(account_uptime).split('.')[0]
        
        account_data.append([
            username,
            account_uptime_str,
            account_stats.get("messages_received", 0),
            account_stats.get("messages_sent", 0),
            account_stats.get("logins", 0),
            len(account_stats.get("games_played", {}))
        ])
    
    if account_data:
        account_table = tabulate(
            account_data,
            headers=["Username", "Uptime", "Msgs Received", "Msgs Sent", "Logins", "Games"],
            tablefmt="grid"
        )
        report.append(account_table)
    else:
        report.append("No account statistics available.")
    
    # Add game statistics
    report.extend([
        "",
        "Game Statistics",
        "--------------"
    ])
    
    game_data = {}
    for username, account_stats in stats["accounts"].items():
        for game_id, count in account_stats.get("games_played", {}).items():
            if game_id not in game_data:
                game_data[game_id] = 0
            game_data[game_id] += count
    
    if game_data:
        game_table_data = [[game_id, count] for game_id, count in 
                          sorted(game_data.items(), key=lambda x: x[1], reverse=True)]
        game_table = tabulate(
            game_table_data,
            headers=["Game ID", "Play Count"],
            tablefmt="grid"
        )
        report.append(game_table)
    else:
        report.append("No game statistics available.")
    
    # Join report into a string
    report_str = "\n".join(report)
    
    # Write to file if requested
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(report_str)
            logger.info(f"Statistics report written to {output_file}")
        except Exception as e:
            logger.error(f"Error writing statistics report: {e}")
    
    return report_str
