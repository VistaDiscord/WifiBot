import discord
from discord import app_commands
import speedtest
import asyncio
import os
import aiohttp
from dotenv import load_dotenv
import logging
import requests
import json

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1161261373628620811
PING_THRESHOLD = 50
SPEED_THRESHOLD = 15
OWNER_IDS = [742066956194152449, 506415483915075594, 531064973116309507, 773238094907834398, 481097139859095572, 493792743072595969]  # Add the actual owner IDs here


intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Creating an instance of the tree to register application commands
tree = app_commands.CommandTree(client)

blocked = False  # global flag to indicate an error that stops operation

async def check_speed():
    global blocked  # ensure we're updating the global variable
    try:
        loop = asyncio.get_running_loop()
        st = speedtest.Speedtest()

        # Wrap the synchronous parts in a thread executor
        await loop.run_in_executor(None, st.get_best_server)
        ping = st.results.ping
        download_speed = await loop.run_in_executor(None, st.download) / (10**6)
        upload_speed = await loop.run_in_executor(None, st.upload) / (10**6)

        return ping, download_speed, upload_speed
    except aiohttp.ClientResponseError as e:
        if e.status == 403:
            blocked = True
            logger.error(f"Access to speedtest.net was blocked with a 403 error: {e}")
        else:
            logger.error(f"Client response error: {e}")
        return None, None, None
    except speedtest.ConfigRetrievalError as e:
        logger.error(f"Speedtest configuration retrieval failed: {e}")
        return None, None, None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None, None, None

async def send_status(channel_id):
    global blocked
    channel = client.get_channel(channel_id)
    if blocked:
        await channel.send("Script is blocked from speedtest.net")
    else:
        ping, download_speed, upload_speed = await check_speed()
        if ping is not None and download_speed is not None and upload_speed is not None:
            # Define the status and color based on the thresholds
            if ping > PING_THRESHOLD or download_speed <= SPEED_THRESHOLD or upload_speed <= SPEED_THRESHOLD:
                status = "Poor"
                color = discord.Color.red()
                description = (
                    "The internet is performing poorly. If you're watching videos, gaming, "
                    "or doing anything that's not school-related, please stop.\n"
                    f"Ping: {ping} ms\n"
                    f"Download Speed: {download_speed:.2f} Mbps\n"
                    f"Upload Speed: {upload_speed:.2f} Mbps"
                )
            else:
                status = "Good"
                color = discord.Color.green()
                description = (
                    f"The internet is performing well.\n"
                    f"Ping: {ping} ms\n"
                    f"Download Speed: {download_speed:.2f} Mbps\n"
                    f"Upload Speed: {upload_speed:.2f} Mbps"
                )

            # Create the embed message for Discord
            embed = discord.Embed(title=f"Network Status: {status}", description=description, color=color)

            # Prepare data for POST request to PHP server
            wifi_data = {
                'ping': ping,
                'download_speed': download_speed,
                'upload_speed': upload_speed,
                'status': status.lower()
            }

            # Send POST request to the PHP endpoint
            try:
                response = requests.post('http://localhost/LiveData/wifi_status.php', json=wifi_data)
                if response.status_code == 200:
                    print("WiFi status updated on server.")
                else:
                    print(f"Failed to update WiFi status: {response.text}")
            except requests.ConnectionError:
                print("Webserver offline, posting to only Discord")
            except requests.RequestException as e:
                print(f"Error sending data to server: {e}")


            # Send the embed message to Discord
            await channel.send(embed=embed)

@tree.command(
    name="speedtest",
    description="Run a speedtest manually"
)
async def speedtest_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await send_status(CHANNEL_ID)
    await interaction.followup.send("Speedtest completed and status sent to the channel.", ephemeral=True)

async def speed_test_scheduler():
    while not blocked:
        await send_status(CHANNEL_ID)
        await asyncio.sleep(600)
    logger.info("The speed test scheduler has been stopped due to a blockage.")

@tree.command(
    name="sync_commands",
    description="Sync all guilds and commands (Bot Owners Only)"
)
async def sync_commands_command(interaction: discord.Interaction):
    # Defer the response if it's going to take some time
    await interaction.response.defer(ephemeral=True)

    # Check if user is an owner
    if interaction.user.id not in OWNER_IDS:
        await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
        return

    try:
        # Sync commands for all guilds
        await tree.sync()
        await interaction.followup.send("Commands synced for all guilds.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)


@tree.command(
    name="change_status",
    description="Change the bot's status (Bot Owners Only)"
)
@app_commands.describe(
    status='The new status to set for the bot',
    twitch_username='Enter your Twitch username (required only for Streaming)'
)
@app_commands.choices(activity_type=[
    app_commands.Choice(name="Playing", value="playing"),
    app_commands.Choice(name="Watching", value="watching"),
    app_commands.Choice(name="Listening", value="listening"),
    app_commands.Choice(name="Streaming", value="streaming")
])
async def change_status_command(interaction: discord.Interaction, status: str, activity_type: app_commands.Choice[str], twitch_username: str = ""):
    # Check if user is an owner
    if interaction.user.id not in OWNER_IDS:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    # Set the activity based on the type
    if activity_type.value == "playing":
        activity = discord.Game(name=status)
    elif activity_type.value == "streaming":
        # For streaming, use the provided Twitch username
        if twitch_username:
            url = f"http://twitch.tv/{twitch_username}"
        else:
            await interaction.response.send_message("Please provide a Twitch username for streaming.", ephemeral=True)
            return
        activity = discord.Streaming(name=status, url=url)
    elif activity_type.value == "listening":
        activity = discord.Activity(type=discord.ActivityType.listening, name=status)
    elif activity_type.value == "watching":
        activity = discord.Activity(type=discord.ActivityType.watching, name=status)

    # Change the bot's status
    await client.change_presence(activity=activity)
    await interaction.response.send_message(f"Status changed to: {activity_type.name} {status}", ephemeral=True)




@client.event
async def on_ready():
    await tree.sync()
    if not blocked:
        asyncio.create_task(speed_test_scheduler())
    logger.info(f'Logged in as {client.user}')
    

client.run(TOKEN)
