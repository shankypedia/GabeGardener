"""
Command-line interface for GabeGardener.

This module provides a CLI using Click for managing GabeGardener.
"""
import os
import sys
import time
import logging
import click

from steamtime.config.settings import load_config, save_config, add_account, remove_account
from steamtime.core.session_manager import SessionManager
from steamtime.utils.logger import setup_logger
from steamtime.utils.stats import generate_stats_report
from steamtime.utils.updater import check_for_updates, VERSION
from steamtime.web.dashboard import start_dashboard

# Setup logger
logger = setup_logger()

@click.group()
@click.version_option(VERSION, prog_name="GabeGardener")
def cli():
    """GabeGardener - Steam Game Hour Booster"""
    # Check for updates
    config = load_config()
    if config.get("auto_update_check", True):
        update_available, latest_version = check_for_updates()
        if update_available:
            click.echo(f"New version available: {latest_version} (current: {VERSION})")
            click.echo("Visit https://github.com/shankypedia/GabeGardener for updates")

@cli.command()
@click.option("--dashboard", is_flag=True, help="Start the web dashboard")
@click.option("--port", type=int, help="Dashboard port (default: 5000)")
def start(dashboard, port):
    """Start boosting sessions"""
    config = load_config()
    
    # Start session manager
    session_manager = SessionManager(config)
    session_manager.start_all_sessions()
    
    # Start dashboard if requested
    if dashboard or config.get("dashboard_enabled", False):
        dashboard_port = port or config.get("dashboard_port", 5000)
        start_dashboard(session_manager, port=dashboard_port)
    
    # Keep the main thread running
    try:
        click.echo("GabeGardener is running. Press Ctrl+C to stop.")
        session_manager.wait_for_sessions()
    except KeyboardInterrupt:
        click.echo("\nShutting down GabeGardener...")
        session_manager.stop_all_sessions()

@cli.command()
@click.option("--port", type=int, help="Dashboard port (default: 5000)")
def dashboard(port):
    """Start only the web dashboard"""
    config = load_config()
    session_manager = SessionManager(config)
    
    dashboard_port = port or config.get("dashboard_port", 5000)
    start_dashboard(session_manager, port=dashboard_port)
    
    try:
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\nShutting down dashboard...")

@cli.command()
def status():
    """Show account status"""
    config = load_config()
    session_manager = SessionManager(config)
    session_manager.print_status()

@cli.command()
@click.argument("username")
@click.argument("password")
@click.option("--games", multiple=True, help="Game IDs to boost")
@click.option("--shared-secret", help="Shared secret for 2FA")
def add_account(username, password, games, shared_secret):
    """Add a new account"""
    game_list = list(games) if games else ["GabeGardener", 730, 440, 570]
    
    # Convert string game IDs to integers
    processed_games = []
    for game in game_list:
        if isinstance(game, str) and game.isdigit():
            processed_games.append(int(game))
        else:
            processed_games.append(game)
    
    add_account(username, password, processed_games, shared_secret)
    click.echo(f"Account {username} added successfully")

@cli.command()
@click.argument("username")
def remove_account(username):
    """Remove an account"""
    remove_account(username)
    click.echo(f"Account {username} removed successfully")

@cli.command()
@click.option("--output", help="Output file for statistics")
def stats(output):
    """Generate statistics report"""
    report = generate_stats_report(output)
    click.echo(report)

@cli.command()
@click.option("--enable/--disable", default=True, help="Enable or disable game rotation")
@click.option("--interval", type=int, help="Rotation interval in seconds")
def rotation(enable, interval):
    """Configure game rotation settings"""
    config = load_config()
    
    config["enable_game_rotation"] = enable
    
    if interval is not None:
        config["rotation_interval"] = interval
    
    save_config(config)
    
    status = "enabled" if enable else "disabled"
    interval_str = f" with interval {config['rotation_interval']} seconds" if enable else ""
    click.echo(f"Game rotation {status}{interval_str}")

@cli.command()
@click.option("--language", help="Set language (e.g., en, es)")
def configure(language):
    """Configure GabeGardener settings"""
    config = load_config()
    
    if language:
        config["language"] = language
        click.echo(f"Language set to {language}")
    
    save_config(config)
    click.echo("Configuration saved")

@cli.command()
def setup():
    """Run interactive setup"""
    click.echo("Starting GabeGardener interactive setup...")
    
    # Import and run quick start script
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from quick_start import create_config
        create_config()
    except ImportError:
        click.echo("Error: Could not find quick_start.py")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli()
