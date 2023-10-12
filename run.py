import discord
import speedtest
import asyncio

# Your bot token goes here
TOKEN = 'TOKEN'
# Your channel ID goes here
CHANNEL_ID = 1161608849334222850
# Your ping threshold in milliseconds
PING_THRESHOLD = 50

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def check_speed():
    st = speedtest.Speedtest()
    st.get_best_server()
    ping = st.results.ping
    return ping

async def send_status(channel_id):
    channel = client.get_channel(channel_id)
    while True:
        ping = await check_speed()
        if ping > PING_THRESHOLD:
            embed = discord.Embed(
                title="Network Status: Poor",
                description=(
                    "The Internet is bad, if you're watching videos, gaming or doing "
                    "anything non-school related please stop.\n"
                    f"Ping: {ping} ms"
                ),
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Network Status: Good",
                description=f"The internet is Fine.\nPing: {ping} ms",
                color=discord.Color.green()
            )

        await channel.send(embed=embed)
        await asyncio.sleep(300)  # Sleep for 5 minutes

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await send_status(CHANNEL_ID)

client.run(TOKEN)
