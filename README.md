# Faceit Match Monitor Bot

This Telegram bot monitors Faceit match statistics for a list of players and sends notifications about their match results. Additionally, it allows users to query player statistics by replying to a bot command with a Faceit username.

## Features

- Monitors Faceit match statistics for a list of predefined players.
- Sends notifications about match results to a specified Telegram chat.
- Allows management of the monitored players list via bot commands.
- Start and stop monitoring with bot commands.

## Configuration

### Telegram Bot Configuration

1. Obtain a Telegram bot token by creating a new bot with the BotFather on Telegram.
2. Replace `YOUR_TELEGRAM_TOKEN` in the script with your Telegram bot token.
3. Replace `YOUR_CHAT_ID` with your Telegram chat ID where the bot should send notifications.

### Faceit API Configuration

1. Obtain a Faceit API key by creating a new application on the Faceit Developer Portal.
2. Replace `YOUR_FACEIT_API_KEY` in the script with your Faceit API key.

### List of Allowed Users
1. Set the ALLOWED_USERS in the .env file with a comma-separated list of Telegram user IDs who are allowed to use the bot commands.

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/hevalito/faceit-match-monitor-bot.git
    cd faceit-match-monitor-bot
    ```

2. Create a `.env` file in the root directory and add your configuration variables:
    ```plaintext
    TELEGRAM_TOKEN=your-telegram-token
    FACEIT_API_KEY=your-faceit-api-key
    CHAT_ID=your-chat-id
    ALLOWED_USERS=user_id1,user_id2,user_id3
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Run the bot:
    ```sh
    python main.py
    ```

## Usage
### Start Monitoring
Use the command /startmonitoring to start monitoring the specified players' matches.

### Stop Monitoring
Use the command /stopmonitoring to stop monitoring the matches.

### List Tracked Players
Use the command /listplayers to list all the players currently being tracked.

### Add a Tracked Player
Use the command /addplayer <Faceit nickname> to add a new player to the tracking list.

### Remove a Tracked Player
Use the command /removeplayer <Faceit nickname> to remove a player from the tracking list.

## Requirements
- Python 3.6+
- python-telegram-bot library
- requests library
- python-dotenv library

## Future Ideas
There are several exciting features planned for future development. Below are some of the future ideas envisioned for the bot:

1. Real-Time Match Notifications: The bot will provide instant notifications when a monitored player starts a new match. 
2. Instant Enemy Profile and Stats Analysis: Upon detecting a new match, the bot will immediately analyze the profiles and statistics of enemy players. 
3. Monitored Players Management via Bot: Users will be able to manage the list of monitored players directly through the bot using specific commands. This functionality will include commands to list all monitored players, add new players, edit player information, and remove players from the monitoring list. 
4. Enhanced Match Statistics: The bot will provide more detailed statistics for monitored matches. This will include advanced metrics and deeper analytical insights.

## License
This project is licensed under the MIT License. See the LICENSE file for details.