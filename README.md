# WiFiBot

WiFiBot is a Discord bot that monitors your network's speed and reports the status to a specified Discord channel. It checks the network speed at regular intervals and informs the users in case the speed falls below a certain threshold.

## Features

- Monitors Ping, Download, and Upload speeds.
- Sends network status updates to a specified Discord channel.
- Alerts when network performance drops below acceptable levels.

## Getting Started

### Prerequisites

- Python 3.8 or newer
- Discord account and a bot token

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/VistaDiscord/WifiBot.git
    cd WifiBot
    ```

2. Install the required dependencies:
    - You'll need to install `discord.py` and `speedtest-cli`. You can do this using pip:
    ```bash
    pip install discord.py speedtest-cli
    ```

3. Create a file named `config.py` in the project directory with the following content:
    ```python
    TOKEN = 'TOKEN'
    CHANNEL_ID = your-discord-channel-id
    ```

4. Replace `'TOKEN'` with your Discord bot token and `your-discord-channel-id` with the ID of the Discord channel where you want to send network status updates.

### Usage

1. Run the bot:
    ```bash
    python run.py
    ```

2. The bot will start monitoring the network speed and send status updates to the specified Discord channel every 5 minutes.

## Configuration

You can customize the bot's behavior by modifying the following variables in `run.py`:

- `PING_THRESHOLD`: The ping threshold in milliseconds above which the network status is considered poor.
- `SPEED_THRESHOLD`: The speed threshold in Mbps below which the network status is considered poor.

## Support

If you encounter any issues or have feature suggestions, please open an issue on GitHub.

## Contributing

Feel free to fork the project, open a Pull Request, or submit issues and feature requests on GitHub.

## License

The project is free to use, and free to duplicate
