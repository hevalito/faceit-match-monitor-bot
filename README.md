# Faceit Match Monitor Bot

This Telegram bot monitors Faceit match statistics for a list of players and sends notifications about their match results. Additionally, it allows users to query player statistics by replying to a bot command with a Faceit username.

## Features

- Monitors Faceit match statistics for a list of predefined players.
- Sends notifications about match results to a specified Telegram chat.

## Configuration

### Telegram Bot Configuration

1. Obtain a Telegram bot token by creating a new bot with the BotFather on Telegram.
2. Replace `YOUR_TELEGRAM_TOKEN` in the script with your Telegram bot token.
3. Replace `YOUR_CHAT_ID` with your Telegram chat ID where the bot should send notifications.

### Faceit API Configuration

1. Obtain a Faceit API key by creating a new application on the Faceit Developer Portal.
2. Replace `YOUR_FACEIT_API_KEY` in the script with your Faceit API key.

### List of Players to Monitor

1. Add or modify the list of Faceit player nicknames in the `FACEIT_PLAYER_NICKNAMES` variable.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/hevalito/faceit-match-monitor-bot.git
cd faceit-match-monitor-bot
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the bot:

```bash
python main.py
```

## Usage
### Start Monitoring
The bot will automatically start monitoring the specified players' matches and send notifications to the configured Telegram chat.

## Requirements
- Python 3.6+
- python-telegram-bot library
- requests library

## Future Ideas
There are several exciting features planned for future development. Below are some of the future ideas envisioned for the bot:

1. Real-Time Match Notifications: The bot will provide instant notifications when a monitored player starts a new match. This feature ensures that users stay up-to-date with the latest activities of their monitored players without any delays.
2. Instant Enemy Profile and Stats Analysis: Upon detecting a new match, the bot will immediately analyze the profiles and statistics of enemy players. This analysis will offer valuable insights into the strengths and weaknesses of opponents, helping users better strategize and prepare for the match.
3. Monitored Players Management via Bot: Users will be able to manage the list of monitored players directly through the bot using specific commands. This functionality will include commands to list all monitored players, add new players, edit player information, and remove players from the monitoring list. Such management capabilities will enhance user convenience by eliminating the need to modify code manually.
4. Enhanced Match Statistics: The bot will provide more detailed statistics for monitored matches. This will include advanced metrics and deeper analytical insights, offering users a comprehensive view of match performance and trends over time.

## License
This project is licensed under the MIT License. See the LICENSE file for details.