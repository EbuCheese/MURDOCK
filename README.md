# Daredevil Discord Bot

This bot sends a random Daredevil YouTube clip to a Discord channel every 24 hours. Users can interact with the clips by saving or blocking them.

## Features
- Sends random Daredevil clips every 24 hours.
- Users can react with 🌟 to favorite or ❌ to block clips.
- Commands: `!daredevil` to fetch a random clip, `!saved` to show saved clips.

## Setup Instructions

### Step 1: Install Dependencies
1. Clone or download this repository.
2. Set up a virtual environment:
    ```bash
    python3 -m venv venv
    ```
3. Activate the virtual environment:
    - **Windows:**
      ```bash
      venv\Scripts\activate
      ```
    - **macOS/Linux:**
      ```bash
      source venv/bin/activate
      ```
4. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Step 2: Configure Your Bot
1. Create a `.env` file in the root directory with the following contents:
    ```txt
    DISCORD_TOKEN=your_discord_bot_token
    YOUTUBE_API_KEY=your_youtube_api_key
    CHANNEL_ID=your_channel_id
    ```
   - Replace `your_discord_bot_token` with your bot's token (from the [Discord Developer Portal](https://discord.com/developers/applications)).
   - Replace `your_youtube_api_key` with your YouTube API key (from the [Google Cloud Console](https://console.cloud.google.com/)).
   - Replace `your_channel_id` with the ID of the channel where the bot should send clips. Right-click the channel in Discord and click "Copy ID."

### Step 3: Run the Bot
1. Run the bot with the following command:
    ```bash
    python bot.py
    ```

2. You should see a confirmation in the terminal when the bot is logged in and running.

### Step 4: Add the Bot to Your Server
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Select your bot application.
3. Under "OAuth2" > "URL Generator", select `bot` as the scope.
4. Under "Bot" > bot permissions select `Send Messages`, `Add Reactions`, `Read Message History`,`Manage Messages`.
5. Copy the generated URL and use it to invite the bot to your server.

### Step 5: Interact with the Bot
- `!daredevil`: Fetch a random Daredevil clip manually.
- `!saved`: Show your saved Daredevil clips.
- React with 🌟 to add a clip to your favorites (saved).
- React with ❌ to block a clip from being shown again.

## Troubleshooting

- Ensure your YouTube API key is valid and that the search queries are correctly configured.
- Make sure the bot has sufficient permissions in your server to read messages, send messages, and add reactions.

## License

This bot is provided under the MIT License. See LICENSE for more details.
