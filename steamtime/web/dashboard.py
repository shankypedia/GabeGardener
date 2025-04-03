"""
Web dashboard module for GabeGardener.

This module provides a web dashboard for monitoring and controlling sessions.
"""
import os
import json
import logging
import threading
from typing import Dict, Any

from flask import Flask, render_template, jsonify, request, redirect, url_for

from steamtime.utils.stats import generate_stats_report
from steamtime.config.settings import load_config, save_config

logger = logging.getLogger("gabegardener")

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Global session manager reference
session_manager = None

def start_dashboard(manager, port=5000):
    """
    Start the web dashboard.
    
    Args:
        manager: Session manager instance
        port (int): Port to run the dashboard on
    """
    global session_manager
    session_manager = manager
    
    # Start Flask in a separate thread
    dashboard_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    )
    dashboard_thread.daemon = True
    dashboard_thread.start()
    
    logger.info(f"Web dashboard started on port {port}")
    print(f"\nWeb dashboard available at: http://localhost:{port}")

@app.route('/')
def index():
    """Render the dashboard index page."""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint for session status."""
    if not session_manager:
        return jsonify({"error": "Session manager not initialized"}), 500
    
    status_list = session_manager.get_session_status()
    return jsonify(status_list)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics."""
    try:
        stats_report = generate_stats_report()
        return jsonify({"stats": stats_report})
    except Exception as e:
        logger.error(f"Error generating stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['GET'])
def api_get_config():
    """API endpoint to get configuration."""
    try:
        config = load_config()
        
        # Remove sensitive information
        for account in config.get("accounts", []):
            if "password" in account:
                account["password"] = "********"
            if "shared_secret" in account:
                account["shared_secret"] = "********" if account["shared_secret"] else ""
        
        return jsonify(config)
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/restart', methods=['POST'])
def api_restart():
    """API endpoint to restart sessions."""
    if not session_manager:
        return jsonify({"error": "Session manager not initialized"}), 500
    
    try:
        session_manager.stop_all_sessions()
        session_manager.start_all_sessions()
        return jsonify({"success": True, "message": "Sessions restarted"})
    except Exception as e:
        logger.error(f"Error restarting sessions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """API endpoint to stop sessions."""
    if not session_manager:
        return jsonify({"error": "Session manager not initialized"}), 500
    
    try:
        session_manager.stop_all_sessions()
        return jsonify({"success": True, "message": "Sessions stopped"})
    except Exception as e:
        logger.error(f"Error stopping sessions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/start', methods=['POST'])
def api_start():
    """API endpoint to start sessions."""
    if not session_manager:
        return jsonify({"error": "Session manager not initialized"}), 500
    
    try:
        session_manager.start_all_sessions()
        return jsonify({"success": True, "message": "Sessions started"})
    except Exception as e:
        logger.error(f"Error starting sessions: {e}")
        return jsonify({"error": str(e)}), 500
