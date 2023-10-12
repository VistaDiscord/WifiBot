import discord
import speedtest
import asyncio

# Your bot token goes here
TOKEN = 'TOKEN'
# Your channel ID goes here
CHANNEL_ID = 1161608849334222850
# Your ping threshold in milliseconds
PING_THRESHOLD = 50
# Your speed thresholds in Mbps
SPEED_THRESHOLD = 10

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def check_speed():
    st = speedtest.Speedtest()
    st.get_best_server()
    ping = st.results.ping
    # Convert speeds from bits per second to megabits per second
    download_speed = st.download() / 10**6
    upload_speed = st.upload() / 10**6
    return ping, download_speed, upload_speed

async def send_status(channel_id):
    channel = client.get_channel(channel_id)
    while True:
        ping, download_speed, upload_speed = await check_speed()
        if ping > PING_THRESHOLD or download_speed <= SPEED_THRESHOLD or upload_speed <= SPEED_THRESHOLD:
            embed = discord.Embed(
                title="Network Status: Poor",
                description=(
                    "The Internet is bad, if you're watching videos, gaming or doing "
                    "anything non-school related please stop.\n"
                    f"Ping: {ping} ms\n"
                    f"Download Speed: {download_speed:.2f} Mbps\n"
                    f"Upload Speed: {upload_speed:.2f} Mbps"
                ),
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Network Status: Good",
                description=(
                    f"The internet is Fine.\n"
                    f"Ping: {ping} ms\n"
                    f"Download Speed: {download_speed:.2f} Mbps\n"
                    f"Upload Speed: {upload_speed:.2f} Mbps"
                ),
                color=discord.Color.green()
            )

        await channel.send(embed=embed)
        await asyncio.sleep(1)  # Sleep for 5 minutes

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await send_status(CHANNEL_ID)

client.run(TOKEN)
