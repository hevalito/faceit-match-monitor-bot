import asyncio
import time
import requests
import logging
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime, timezone
from dateutil.parser import isoparse
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Configurations
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
FACEIT_API_KEY = os.getenv('FACEIT_API_KEY')
CHAT_ID = os.getenv('CHAT_ID')
ALLOWED_USERS = list(map(int, os.getenv('ALLOWED_USERS', '').split(',')))  # Parse as list of integers

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

not_allowed_text = "You're not authorized for this command."

# check for tg user ID if added to admin list
def is_user_allowed(update: Update):
    user_id = update.effective_user.id
    return user_id in ALLOWED_USERS

# Load players from JSON file
def load_players():
    try:
        with open('players.json', 'r') as file:
            data = json.load(file)
            return data['players']
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_headers():
    return {'Authorization': f'Bearer {FACEIT_API_KEY}'}

# Accesses Faceit Statuspage to get the current status
def get_faceit_status():
    status_emojis = {
        "full_outage": "🔴",
        "partial_outage": "🟠",
        "under_maintenance": "🟡",
        "degraded_performance": "🟣",
        "operational": "🟢"
    }

    try:
        response_summary = requests.get('https://www.faceitstatus.com/proxy/www.faceitstatus.com')
        response_summary.raise_for_status()
        summary_data = response_summary.json()

        response_incidents = requests.get(
            'https://www.faceitstatus.com/proxy/www.faceitstatus.com/component_impacts?start_at=2024-02-23T23%3A59%3A59.999Z&end_at=2024-05-24T23%3A59%3A59.999Z'
        )
        response_incidents.raise_for_status()
        incidents_data = response_incidents.json()

        components = summary_data['summary']['components']
        component_impacts = incidents_data['component_impacts']
        ongoing_incidents = []

        # Filter ongoing incidents
        for impact in component_impacts:
            end_at = impact['end_at']
            if not end_at or isoparse(end_at) > datetime.now(timezone.utc):
                ongoing_incidents.append(impact)

        status_summary = "<b>FACEIT Status:</b>\n"
        for component in components:
            component_name = component['name']
            component_id = component['id']
            component_status = "operational"  # Default status

            for impact in ongoing_incidents:
                if impact['component_id'] == component_id:
                    component_status = impact['status']
                    break

            emoji = status_emojis.get(component_status, "🟢")
            status_summary += f"{emoji} {component_name}: {component_status.replace('_', ' ').title()}\n"

        if not ongoing_incidents:
            status_summary += "\nAll systems are operational."

        return status_summary

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching FACEIT status: {e}")
        return "<b>Error fetching FACEIT status.</b>"


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

monitoring_task = None

async def start_monitoring(update, context):
    if not is_user_allowed(update):
        await update.message.reply_text(not_allowed_text)
        return
    
    global monitoring_task
    if monitoring_task is None or monitoring_task.cancelled():
        monitoring_task = asyncio.create_task(monitor_players())
        await update.message.reply_text("Monitoring started.")
    else:
        await update.message.reply_text("Monitoring is already running.")

async def stop_monitoring(update, context):
    if not is_user_allowed(update):
        await update.message.reply_text(not_allowed_text)
        return
    
    global monitoring_task
    if monitoring_task and not monitoring_task.cancelled():
        monitoring_task.cancel()
        await update.message.reply_text("Monitoring stopped.")
    else:
        await update.message.reply_text("Monitoring is not running.")

async def status(update, context):
    if not is_user_allowed(update):
        await update.message.reply_text(not_allowed_text)
        return

    monitoring_status = "active" if monitoring_task and not monitoring_task.cancelled() else "inactive"
    tracked_players = load_players()
    num_tracked_players = len(tracked_players)
    faceit_status = get_faceit_status()

    status_message = (
        f"<b>Bot Status:</b>\n"
        f"Monitoring is currently <b>{monitoring_status}</b>.\n"
        f"Number of players being tracked: <b>{num_tracked_players}</b>.\n\n"
        f"{faceit_status}"
    )
    
    await update.message.reply_text(status_message, parse_mode=ParseMode.HTML)

# Async function to monitor players (60s loop currently)
async def monitor_players():
    player_nicknames = load_players()
    player_ids = {nickname: get_player_id_by_nickname(nickname) for nickname in player_nicknames}
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

async def list_players(update, context):
    if not is_user_allowed(update):
        await update.message.reply_text(not_allowed_text)
        return

    players = load_players()
    if players:
        await update.message.reply_text("Players being tracked:\n" + "\n".join(players))
    else:
        await update.message.reply_text("No players are currently being tracked.")

async def add_player(update, context):
    if not is_user_allowed(update):
        await update.message.reply_text(not_allowed_text)
        return

    try:
        nickname = context.args[0]  # Get the nickname from the command arguments
        player_id = get_player_id_by_nickname(nickname)  # Check if the player exists

        players = load_players()
        if nickname not in players:
            players.append(nickname)
            with open('players.json', 'w') as file:
                json.dump({'players': players}, file)
            await update.message.reply_text(f"Player '{nickname}' added successfully!")
        else:
            await update.message.reply_text(f"Player '{nickname}' is already being tracked.")
    except IndexError:
        await update.message.reply_text("Usage: /addplayer <Faceit nickname>")
    except requests.exceptions.HTTPError:
        await update.message.reply_text("Player not found on FACEIT.")

async def remove_player(update, context):
    if not is_user_allowed(update):
        await update.message.reply_text(not_allowed_text)
        return

    try:
        nickname = context.args[0]  # Get the nickname from the command arguments
        players = load_players()
        if nickname in players:
            players.remove(nickname)
            with open('players.json', 'w') as file:
                json.dump({'players': players}, file)
            await update.message.reply_text(f"Player '{nickname}' removed successfully!")
        else:
            await update.message.reply_text(f"Player '{nickname}' not found in the tracking list.")
    except IndexError:
        await update.message.reply_text("Usage: /removeplayer <Faceit nickname>")

# Main function
if __name__ == '__main__':
    try:
        # Create application
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        # Register command handlers
        application.add_handler(CommandHandler("listplayers", list_players))
        application.add_handler(CommandHandler("addplayer", add_player))
        application.add_handler(CommandHandler("removeplayer", remove_player))
        application.add_handler(CommandHandler("startmonitoring", start_monitoring))
        application.add_handler(CommandHandler("stopmonitoring", stop_monitoring))
        application.add_handler(CommandHandler("status", status))

        # Start the bot
        application.run_polling()
    except Exception as e:
        logger.error(f'Error in main loop: {e}')
