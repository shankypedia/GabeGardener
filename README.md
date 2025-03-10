# GabeGardener

A modern, efficient utility for managing Steam game sessions across multiple accounts.

<!-- ![GabeGardener Logo](https://i.imgur.com/logo.png) -->

## 🌱 What is GabeGardener?

GabeGardener helps you manage multiple Steam accounts and boost your game hours automatically. It's designed to be easy to use, even for non-technical users, while providing powerful features for advanced users.

## ✨ Features

- **Multi-Account Support**: Manage multiple Steam accounts simultaneously
- **Game Session Management**: Run up to 32 games per account
- **Flexible Status Options**: Custom online status and game display
- **Secure Authentication**: Support for Steam Guard and 2FA
- **Message Management**: Auto-reply to messages and optional message logging
- **Persistent Sessions**: Automatic session recovery and login key management
- **Web Dashboard**: Monitor and control your sessions through a web interface
- **Game Rotation**: Automatically rotate through your game library
- **Statistics Tracking**: Track uptime, messages, and other metrics
- **Command-Line Interface**: Full control through an intuitive CLI
- **Internationalization**: Support for multiple languages
- **Enhanced Security**: Password encryption for configuration files
- **Auto-Update Checking**: Stay up to date with the latest features

## 🚀 Quick Start

### For Beginners

The easiest way to get started is to use our Quick Start Wizard:

1. Make sure you have Python 3.7+ installed
2. Download GabeGardener
3. Run the Quick Start Wizard:

```bash
python quick_start.py
```

4. Follow the prompts to set up your accounts
5. Start GabeGardener:

```bash
python main.py
```

### For Advanced Users

If you prefer to set things up manually:

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Create a configuration file at `~/.gabegardener/config.json`
3. Start GabeGardener:

```bash
python main.py start
```

## 📋 Usage

### Command-Line Interface

GabeGardener provides a comprehensive CLI:

```bash
# Start all sessions
python main.py start

# Start with web dashboard
python main.py start --dashboard

# Show account status
python main.py status

# Add a new account
python main.py add-account username password --games 730 440 570

# Remove an account
python main.py remove-account username

# Generate statistics report
python main.py stats --output report.txt

# Start only the web dashboard
python main.py dashboard --port 8080
```

### Web Dashboard

The web dashboard provides a user-friendly interface for monitoring and controlling your sessions. Access it by starting with the `--dashboard` flag or using the `dashboard` command.

<!-- ![Dashboard Screenshot](https://i.imgur.com/dashboard.png) -->

## ⚙️ Configuration

GabeGardener uses a configuration file located at `~/.gabegardener/config.json`. If this file doesn't exist, default settings will be used.

You can create this file manually with the following structure:

```json
{
  "show_timer": true,
  "enable_game_rotation": false,
  "rotation_interval": 3600,
  "language": "en",
  "auto_update_check": true,
  "dashboard_enabled": true,
  "dashboard_port": 5000,
  "accounts": [
    {
      "username": "your_username",
      "password": "your_password",
      "shared_secret": "",
      "visible": true,
      "games": [
        "GabeGardener",
        730,
        440,
        570
      ],
      "auto_reply": "I am currently AFK. This is an automated message.",
      "receive_messages": false,
      "save_messages": false,
      "game_rotation": false,
      "rotation_interval": null
    }
  ]
}
```

### Account Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `username` | string | Steam account username |
| `password` | string | Steam account password |
| `shared_secret` | string | Shared secret for 2FA (optional) |
| `visible` | boolean | Whether to appear online (true) or invisible (false) |
| `games` | array | List of game IDs and/or status message |
| `auto_reply` | string | Message to automatically reply with (optional) |
| `receive_messages` | boolean | Whether to log received messages |
| `save_messages` | boolean | Whether to save received messages to files |
| `game_rotation` | boolean | Whether to enable game rotation for this account |
| `rotation_interval` | number | Custom rotation interval in seconds (optional) |

## 🔒 Security Notes

- Login keys are stored in `~/.gabegardener/login_keys/` with secure permissions
- Passwords are stored encrypted in the configuration file
- Consider using environment variables for sensitive information in production environments

## 🌐 Internationalization

GabeGardener supports multiple languages. To change the language, set the `language` option in your configuration file to one of the supported language codes:

- `en` - English
- `es` - Spanish

## 🖥️ Deployment Options

GabeGardener can be deployed in various environments:

- **Windows/macOS/Linux**: Run directly with Python
- **Docker**: Use our Docker image for containerized deployment
- **Pterodactyl Panel**: Use our custom egg for game server panels
- **Raspberry Pi**: Perfect for 24/7 low-power operation
- **Cloud Services**: Deploy to Heroku, AWS, Google Cloud, etc.

See our [Production Setup Guide](production_setup.md) for detailed instructions for each deployment option.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Steam](https://store.steampowered.com/) for the platform
- [steam-py](https://github.com/ValvePython/steam) for the Python Steam client
- All contributors and users of GabeGardener
