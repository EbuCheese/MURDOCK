# Daredevil Discord Bot

This is a Discord bot that sends a daily random Daredevil clip to a specified channel, allows users to react to clips to save or block them, and retrieve saved clips using commands.

## Features
- Sends a random Daredevil YouTube clip every 24 hours.
- Users can react with 🌟 to save clips to their favorites or ❌ to block clips from being shown again.
- Supports the `!daredevil` command to get a random clip manually.
- Supports the `!saved` command to show the user's favorite clips.

## Requirements

- Python 3.8 or higher
- A Discord bot token
- A YouTube API key (for fetching random clips)
- A Discord channel ID to send the clips to

## Setup Instructions

### Step 1: Install Python and Dependencies
Make sure you have Python 3.8 or higher installed. You can download it from [here](https://www.python.org/downloads/).

1. Clone or download this repository.
2. Navigate to the project folder and create a virtual environment:
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
4. Install the required dependencies by running:
    ```bash
    pip install -r requirements.txt
    ```

### Step 2: Set Up Your Environment Variables

Create a `.env` file in the root directory of the project and add your bot token and YouTube API key. The `.env` file should look like this:

```txt
DISCORD_TOKEN=your_discord_bot_token
YOUTUBE_API_KEY=your_youtube_api_key
CHANNEL_ID=your_channel_id
