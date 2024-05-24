import asyncio
import time
import requests
import logging
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configurations
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
FACEIT_API_KEY = os.getenv('FACEIT_API_KEY')
CHAT_ID = os.getenv('CHAT_ID')
FACEIT_PLAYER_NICKNAMES = ['baboheval', 'Swarrish', 'sabunu', 'burrrrq', 'Spoon2Moon', 'dA_K0vac', 'Mush_Mush_', '-_HeaveN', 'botdns', 'PSYCHO-DAN', 'xXtini95Xx']  # List of player IDs to monitor

# Map image URLs
MAP_IMAGES = {
    'de_dust2': 'https://static.wikia.nocookie.net/counterstrike/images/2/2e/Dust2_CS2.png',
    'de_mirage': 'https://static.wikia.nocookie.net/counterstrike/images/e/e5/Mirage_CS2.png',
    'de_nuke': 'https://static.wikia.nocookie.net/counterstrike/images/9/9d/Nuke_CS2.png',
    'de_overpass': 'https://static.wikia.nocookie.net/counterstrike/images/f/f9/Overpass_CS2.png',
    'de_vertigo': 'https://static.wikia.nocookie.net/counterstrike/images/c/cb/Vertigo_CS2.png',
    'de_ancient': 'https://static.wikia.nocookie.net/counterstrike/images/7/7f/Ancient_CS2.png',
    'de_inferno': 'https://static.wikia.nocookie.net/counterstrike/images/8/82/Inferno_CS2.png',
    'de_anubis': 'https://static.wikia.nocookie.net/counterstrike/images/7/70/Anubis_CS2.png',
    'cs_office': 'https://static.wikia.nocookie.net/counterstrike/images/e/ee/Office_CS2.png',
    # Add other maps as necessary
}

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot
bot = Bot(token=TELEGRAM_TOKEN)

def get_headers():
    return {'Authorization': f'Bearer {FACEIT_API_KEY}'}

# Gets player ID by nickname from Faceit Endpoint
def get_player_id_by_nickname(nickname):
    response = requests.get(f'https://open.faceit.com/data/v4/players?nickname={nickname}', headers=get_headers())
    response.raise_for_status()
    return response.json().get('player_id')

# Gets recent Matches of player by Player ID
def get_recent_matches(player_id):
    response = requests.get(f'https://open.faceit.com/data/v4/players/{player_id}/history', headers=get_headers())
    response.raise_for_status()
    return response.json()

# Gets stats of a match by match ID
def get_match_details(match_id):
    response = requests.get(f'https://open.faceit.com/data/v4/matches/{match_id}/stats', headers=get_headers())
    response.raise_for_status()
    logger.info(response.json())
    return response.json()

# Gets data of a match by match ID
def get_additional_match_details(match_id):
    response = requests.get(f'https://open.faceit.com/data/v4/matches/{match_id}', headers=get_headers())
    response.raise_for_status()
    return response.json()

# Generates a monospace table with the given player data
def generate_player_stats_table(player_stats):
    header = "<pre><b>Player          K  D  K/DR  KR</b>\n"
    table = header + "\n".join([
        f"{stats['nickname']:<15} {stats['kills']:<2} {stats['deaths']:<2} {stats['kd_ratio']:<5} {stats['kr']:<5}"
        for stats in player_stats
    ]) + "</pre>"
    return table

# Gets the most recent match of a player
def get_last_match_id(player_id):
    matches = get_recent_matches(player_id)
    if matches['items']:
        return matches['items'][0]['match_id']
    return None

# Sends a message via bot
async def send_message(chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)

# Async function to monitor players (60s loop currently)
async def monitor_players():
    player_ids = {nickname: get_player_id_by_nickname(nickname) for nickname in FACEIT_PLAYER_NICKNAMES}
    last_match_ids = {player_id: None for player_id in player_ids.values()}
    notified_matches = set()

    while True:
        matches_to_notify = []
        for nickname, player_id in player_ids.items():
            try:
                last_match_id = get_last_match_id(player_id)
                if last_match_id and last_match_id not in notified_matches:
                    matches_to_notify.append((nickname, player_id, last_match_id))
            except Exception as e:
                logger.error(f'Error retrieving or sending match info for player {nickname} (ID: {player_id}): {e}')

        match_groups = {}
        for nickname, player_id, match_id in matches_to_notify:
            if match_id not in match_groups:
                match_groups[match_id] = []
            match_groups[match_id].append((nickname, player_id))

        for match_id, players in match_groups.items():
            try:
                match_details = get_match_details(match_id)
                additional_details = get_additional_match_details(match_id)
                logger.info(f"Match details: {match_details}")

                if 'rounds' in match_details and match_details['rounds']:
                    round_data = match_details['rounds'][0]
                    result = round_data['round_stats']['Winner']
                    rounds = round_data['round_stats']['Rounds']
                    map_played = round_data['round_stats']['Map']
                    demo_url = additional_details['demo_url'][0] if 'demo_url' in additional_details and additional_details['demo_url'] else 'N/A'

                    start_time = datetime.fromtimestamp(additional_details['started_at']).strftime('%Y-%m-%d %H:%M:%S')
                    duration_minutes = (additional_details['finished_at'] - additional_details['started_at']) // 60

                    player_stats = []
                    player_team = None

                    for team in round_data['teams']:
                        for player in team['players']:
                            if player['player_id'] in [player_id for _, player_id in players]:
                                player_team = team['team_id']
                                player_stats.append({
                                    'nickname': player['nickname'],
                                    'kills': player['player_stats'].get('Kills', 'N/A'),
                                    'deaths': player['player_stats'].get('Deaths', 'N/A'),
                                    'kd_ratio': player['player_stats'].get('K/D Ratio', 'N/A'),
                                    'kr': player['player_stats'].get('K/R Ratio', 'N/A')
                                })

                    match_result = '🟩 Won' if result == player_team else '🟥 Lost'
                    player_stats_table = generate_player_stats_table(player_stats)

                    message = (
                        f"<b>New Match Played!</b>\n"
                        f"<b>Match ID:</b> <a href='https://www.faceit.com/en/cs2/room/{match_id}'>{match_id}</a>\n"
                        f"<b>Result:</b> <b>{match_result}</b>\n"
                        f"<b>Rounds:</b> {rounds}\n"
                        f"<b>Map:</b> {map_played}\n"
                        f"<b>Time:</b> {start_time}\n"
                        f"<b>Duration:</b> {duration_minutes} minutes\n"
                        f"<b>Demo:</b> <a href='{demo_url}'>Watch Here</a>\n\n"
                        f"{player_stats_table}"
                    )

                    await send_message(chat_id=CHAT_ID, text=message)
                    logger.info(f'Notified new match with ID {match_id} for players: {", ".join([nickname for nickname, _ in players])}')
                    notified_matches.add(match_id)

            except Exception as e:
                logger.error(f'Error processing match {match_id}: {e}')

        await asyncio.sleep(60)

# Main function
if __name__ == '__main__':
    try:
        asyncio.run(monitor_players())
    except Exception as e:
        logger.error(f'Error in monitoring players: {e}')