import os
import sys
import time
from src.hour_booster import build_bot
from config.accounts import configs_array

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n* Detected {len(configs_array)} account(s) in the config.")
    
    bot_array = []
    
    for i, config in enumerate(configs_array):
        # Check if too many games are configured
        if len(config['games_and_status']) > 32:
            print(f"* An error has occurred, account #{i} has more than 32 games in the list.")
            print("* (If you want to boost exactly 32 games, you might consider replacing the String of the custom status with the Integer (ID) of one game.)\n")
            sys.exit(1)
        
        # Create and start bot
        bot = build_bot(config)
        bot.do_login()
        bot_array.append(bot)
    
    print(f"* Starting idling {len(bot_array)} account(s).\n* Press CTRL + C to exit.\n")
    
    # Keep the script running
    try:
        start_time = time.time()
        while True:
            if clock:
                elapsed = time.time() - start_time
                hours, remainder = divmod(int(elapsed), 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"* Timer: {hours:02d}:{minutes:02d}:{seconds:02d}"
                print(time_str, end='\r')
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
