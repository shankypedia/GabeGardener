#!/usr/bin/env python3
"""
GabeGardener - Steam Game Hour Booster

This is the main entry point for the GabeGardener application.
It handles command-line arguments and starts the appropriate services.
"""
import os
import sys
import argparse
import logging
from steamtime.config.settings import load_config
from steamtime.core.session_manager import SessionManager
from steamtime.utils.logger import setup_logger
from steamtime.web.dashboard import start_dashboard
from steamtime.cli.commands import cli

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="GabeGardener - Steam Game Hour Booster")
    
    # Main commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start boosting sessions")
    start_parser.add_argument("--dashboard", action="store_true", help="Start the web dashboard")
    start_parser.add_argument("--port", type=int, help="Dashboard port (default: 5000)")
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Start only the web dashboard")
    dashboard_parser.add_argument("--port", type=int, help="Dashboard port (default: 5000)")
    
    # Status command
    subparsers.add_parser("status", help="Show account status")
    
    # Add account command
    add_account_parser = subparsers.add_parser("add-account", help="Add a new account")
    add_account_parser.add_argument("username", help="Steam username")
    add_account_parser.add_argument("password", help="Steam password")
    add_account_parser.add_argument("--games", nargs="+", help="Game IDs to boost")
    add_account_parser.add_argument("--shared-secret", help="Shared secret for 2FA")
    
    # Remove account command
    remove_account_parser = subparsers.add_parser("remove-account", help="Remove an account")
    remove_account_parser.add_argument("username", help="Steam username to remove")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Generate statistics report")
    stats_parser.add_argument("--output", help="Output file for statistics")
    
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    # Check if running as CLI module
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        sys.argv.pop(1)  # Remove 'cli' argument
        cli()
        return

    # Setup logger
    setup_logger()
    logger = logging.getLogger("gabegardener")
    
    # Parse arguments
    args = parse_arguments()
    
    # Load configuration
    config = load_config()
    
    # Handle commands
    if args.command == "start":
        # Start session manager
        session_manager = SessionManager(config)
        session_manager.start_all_sessions()
        
        # Start dashboard if requested
        if args.dashboard or config.get("dashboard_enabled", False):
            port = args.port or config.get("dashboard_port", 5000)
            start_dashboard(session_manager, port=port)
        else:
            # Keep the main thread running
            try:
                session_manager.wait_for_sessions()
            except KeyboardInterrupt:
                logger.info("Shutting down GabeGardener...")
                session_manager.stop_all_sessions()
    
    elif args.command == "dashboard":
        # Start only the dashboard
        session_manager = SessionManager(config)
        port = args.port or config.get("dashboard_port", 5000)
        start_dashboard(session_manager, port=port)
    
    elif args.command == "status":
        # Show account status
        session_manager = SessionManager(config)
        session_manager.print_status()
    
    elif args.command == "add-account":
        # Add a new account
        from steamtime.config.settings import add_account
        games = args.games if args.games else ["GabeGardener", 730, 440, 570]
        add_account(args.username, args.password, games, args.shared_secret)
        logger.info(f"Account {args.username} added successfully")
    
    elif args.command == "remove-account":
        # Remove an account
        from steamtime.config.settings import remove_account
        remove_account(args.username)
        logger.info(f"Account {args.username} removed successfully")
    
    elif args.command == "stats":
        # Generate statistics report
        from steamtime.utils.stats import generate_stats_report
        output_file = args.output
        generate_stats_report(output_file)
    
    else:
        # No command specified, show help
        parse_arguments()

if __name__ == "__main__":
    main()
