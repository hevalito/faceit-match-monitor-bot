# Faceit Match Monitor Bot

This Telegram bot monitors Faceit match statistics for a list of players and sends notifications about their match results. It offers management of the tracked user via bot commands and contains a small access management feature, so that only given users can command the bot.

![Telegram](https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Telegram_2019_Logo.svg/120px-Telegram_2019_Logo.svg.png)

![Faceit](https://upload.wikimedia.org/wikipedia/commons/8/89/FaceIT_banner.png)

## Features

- Monitors FACEIT match statistics for a list of predefined players. 
- Sends notifications about match results to a specified Telegram chat.
- Allows management of the monitored players list via bot commands.
- Start and stop monitoring with bot commands.
- Gets Faceit Service Status from faceitstatus.com and informs the user of The Bot's status

## Configuration
### Telegram Bot Configuration

1. Obtain a Telegram bot token by creating a new bot with the @BotFather on Telegram. 
*Optional:* Propagate the possible commands of your bot to BotFather, so that you can select one of the possible commands in the chat inline. Use this template for this after you've used /setcommands with BotFather: 
```plaintext
listplayers - Lists all tracked players
addplayer - Add another FACEIT Nickname to be tracked by the bot
removeplayer - Remove a player from tracked players
startmonitoring - Starts the monitoring for given FACEIT users
stopmonitoring - Stops monitoring for new FACEIT matches of given users.
status - gets current FACEIT status and Bot Monitoring status
```
3. Get your Telegram bot token from BotFather. You will add this to the .env File in the Setup process as `TELEGRAM_TOKEN`
4. Get the Chat ID of a group chat, or a chat session with the bot where the bot should send notifications to. This will be added as `CHAT_ID`to the .env File.

### Faceit API Configuration
1. Obtain a FACEIT API key by creating a new application on the FACEIT Developer Portal.
2. Replace `YOUR_FACEIT_API_KEY` in the script with your FACEIT API key.
### List of Allowed Users
1. Set the ALLOWED_USERS in the .env file with a comma-separated list of Telegram user IDs who are allowed to use the bot commands.

## Setup

1. Clone the repository:
```sh
git clone https://github.com/hevalito/faceit-match-monitor-bot.git
cd faceit-match-monitor-bot
```
2. Create an `.env` file in the root directory and add your configuration variables:
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
Use the command `/startmonitoring` to start monitoring the specified players' matches.

### Stop Monitoring
Use the command `/stopmonitoring` to stop monitoring the matches.

### List Tracked Players
Use the command `/listplayers` to list all the players currently being tracked.

### Add a Tracked Player
Use the command `/addplayer <Faceit nickname>` to add a new player to the tracking list.

### Remove a Tracked Player
Use the command `/removeplayer <Faceit nickname>` to remove a player from the tracking list.

### Check Bot and FACEIT Status
Use the command `/status` to get a real time status update of the FACEIT Services and know about the Bot's monitoring status

## Requirements
- Python 3.6+
- python-telegram-bot library
- requests library
- python-dotenv library

## Future Ideas
There are several exciting features planned for future development. Below are some of the future ideas envisioned for the bot:

1. Real-Time Match Notifications: The bot will provide instant notifications when a monitored player starts a new match.
2. Instant Enemy Profile and Stats Analysis: Upon detecting a new match, the bot will immediately analyze the profiles and statistics of enemy players.
3. ~~Monitored Players Management via Bot: Users will be able to manage the list of monitored players directly through the bot using specific commands. This functionality will include commands to list all monitored players, add new players, edit player information, and remove players from the monitoring list.~~ DONE!
4. Enhanced Match Statistics: The bot will provide more detailed statistics for monitored matches. This will include advanced metrics and deeper analytical insights.

## License
This project is licensed under the MIT License. See the LICENSE file for details.