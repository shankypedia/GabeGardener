#!/bin/bash
# GabeGardener - Pterodactyl startup script

# Create config directory if it doesn't exist
mkdir -p ~/.gabegardener

# Check if config exists, create if not
if [ ! -f ~/.gabegardener/config.json ]; then
    echo "Creating default configuration..."
    cat > ~/.gabegardener/config.json << EOL
{
  "show_timer": true,
  "enable_game_rotation": false,
  "rotation_interval": 3600,
  "language": "en",
  "auto_update_check": false,
  "dashboard_port": ${DASHBOARD_PORT:-5000},
  "dashboard_enabled": ${DASHBOARD_ENABLED:-true},
  "accounts": [
    {
      "username": "${STEAM_USERNAME}",
      "password": "${STEAM_PASSWORD}",
      "shared_secret": "${STEAM_SHARED_SECRET}",
      "visible": true,
      "games": [
        "GabeGardener",
        730,
        440,
        570
      ],
      "auto_reply": "I am currently AFK. This is an automated message.",
      "receive_messages": true,
      "save_messages": true,
      "game_rotation": false
    }
  ]
}
EOL
    chmod 600 ~/.gabegardener/config.json
fi

# Install dependencies if needed
pip install -r requirements.txt

# Set environment variables for the application
export GABEGARDENER_DASHBOARD=${DASHBOARD_ENABLED:-true}
export GABEGARDENER_DASHBOARD_PORT=${DASHBOARD_PORT:-5000}
export GABEGARDENER_CONFIG=~/.gabegardener/config.json

# Start the application
python main.py
