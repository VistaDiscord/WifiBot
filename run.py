import discord
import speedtest
import asyncio
import aiohttp

TOKEN = 'TOKEN'
CHANNEL_ID = 1161261373628620811
PING_THRESHOLD = 50
SPEED_THRESHOLD = 15

intents = discord.Intents.default()
client = discord.Client(intents=intents)

blocked = False  # global flag to indicate a 403 error

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
            return None, None, None  # return None values if a 403 error occurs
        raise  # re-raise the exception if it's not a 403 error

async def send_status(channel_id):
    channel = client.get_channel(channel_id)
    while True:
        if blocked:
            await channel.send("Script is blocked from speedtest.net")
        else:
            ping, download_speed, upload_speed = await check_speed()
            if ping is not None and download_speed is not None and upload_speed is not None:
                if ping > PING_THRESHOLD or download_speed <= SPEED_THRESHOLD or upload_speed <= SPEED_THRESHOLD:
                    embed = discord.Embed(
                        title="Netwerkstatus: Slecht",
                        description=(
                            "Het internet is slecht. Als je video's kijkt, aan het gamen bent of "
                            "iets doet dat niet schoolgerelateerd is, stop dan alsjeblieft.\n"
                            f"Ping: {ping} ms\n"
                            f"Download Speed: {download_speed:.2f} Mbps\n"
                            f"Upload Speed: {upload_speed:.2f} Mbps"
                        ),
                        color=discord.Color.red()
                    )
                else:
                    embed = discord.Embed(
                        title="Netwerkstatus: Goed",
                        description=(
                            f"Het internet is prima.\n"
                            f"Ping: {ping} ms\n"
                            f"Download Speed: {download_speed:.2f} Mbps\n"
                            f"Upload Speed: {upload_speed:.2f} Mbps"
                        ),
                        color=discord.Color.green()
                    )
                await channel.send(embed=embed)
        await asyncio.sleep(600)  # Sleep for 10 minutes

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await send_status(CHANNEL_ID)

client.run(TOKEN)
