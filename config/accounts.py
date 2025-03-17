configs_array = []

# 1st Account (you can boost many accounts as you want)
config = {
    'username': 'username',  # Account username
    'password': 'password',  # Account password
    'shared_secret': '',  # Shared secret (2FA only), leave it blank for steam guard code
    'enable_status': True,  # Set it to false if you want to stay invisible
    'games_and_status': [
        'Boosting hours...',  # Your custom status (counts as a game, you can only boost 31 games with the custom status)
        730,
        440,
        570,
    ],  # IDs of the games, separated by comma
    'reply_message': '',  # Leave it blank for no reply message
    'receive_messages': False,  # Do you want to log the messages that you receive in the terminal?
    'save_messages': False,  # Do you want to save the messages that you receive in a file?
}
configs_array.append(config)

# 2nd account (you can boost many accounts as you want)
config = {
    'username': 'username',  # Account username
    'password': 'password',  # Account password
    'shared_secret': '',  # Shared secret (2FA only), leave it blank for steam guard code
    'enable_status': True,  # Set it to false if you want to stay invisible
    'games_and_status': [1172470, 730, 440, 570],  # IDs of the games, separated by comma (without the status, this is necessary in case you want to boost 32 games)
    'reply_message': '',  # Leave it blank for no reply message
    'receive_messages': False,  # Do you want to log the messages that you receive in the terminal?
    'save_messages': False,  # Do you want to save the messages that you receive in a file?
}
configs_array.append(config)
