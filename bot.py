import os
import random
import json
import re
import datetime
from dotenv import load_dotenv

import discord
from googleapiclient.discovery import build
from discord.ext import commands, tasks

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

# File paths
SENT_CLIPS_FILE = "sent_clips.json"
BLOCKED_CLIPS_FILE = "blocked_clips.json"
FAVORITE_CLIPS_FILE = "favorite_clips.json"
CHANNEL_MAP_FILE = "channel_map.json"

# Load JSON Data
def load_json(file, default_data):
    if not os.path.exists(file) or os.path.getsize(file) == 0:
        return default_data
    try:
        with open(file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default_data

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# Load search queries from file
def load_search_queries(file_path="search_queries.txt"):
    if not os.path.exists(file_path):
        return ["Daredevil clip"]  # fallback if file not found
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# Load all stored data
sent_clips = load_json(SENT_CLIPS_FILE, {"sent": []})
blocked_clips = load_json(BLOCKED_CLIPS_FILE, {"blocked": []})
favorite_clips = load_json(FAVORITE_CLIPS_FILE, {})
channel_map = load_json(CHANNEL_MAP_FILE, {})

# YouTube Query List from file
SEARCH_QUERIES = load_search_queries()

# logic for getting random Daredevil clip
def get_random_daredevil_clip():
    blocked_ids = set(blocked_clips["blocked"])
    recent_ids = {
        clip["video_id"]
        for clip in sent_clips["sent"]
        if (datetime.datetime.now() - datetime.datetime.fromisoformat(clip["timestamp"])).days < 14
    }

    # 10% chance to send a favorite clip that hasn’t been sent recently or blocked
    if favorite_clips and random.random() < 0.1:
        all_favs = list(set(sum(favorite_clips.values(), [])))  # flatten + dedupe
        random.shuffle(all_favs)

        for url in all_favs:
            video_id = url.split("v=")[-1]
            if video_id in blocked_ids or video_id in recent_ids:
                continue

            # Save the favorite clip as "sent"
            sent_clips["sent"].append({
                "video_id": video_id,
                "timestamp": datetime.datetime.now().isoformat()
            })

            if len(sent_clips["sent"]) > 100:
                sent_clips["sent"] = sent_clips["sent"][-100:]

            save_json(SENT_CLIPS_FILE, sent_clips)
            return url

    # Shuffle the search queries to start with different ones each time
    attempts = 0
    max_attempts = 10
    queries = SEARCH_QUERIES[:]
    random.shuffle(queries)

    while attempts < max_attempts:
        for query in queries:
            response = youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=25
            ).execute()

            videos = response["items"]
            random.shuffle(videos)  # Shuffle the video results

            for item in videos:
                video_id = item["id"]["videoId"]

                # Check if already sent in the last 2 weeks OR blocked
                if video_id in blocked_ids or video_id in recent_ids:
                    continue  # Skip blocked clips / recent clips

                # Save the valid clip
                sent_clips["sent"].append({
                    "video_id": video_id,
                    "timestamp": datetime.datetime.now().isoformat()
                })

                # Keep the last 100 clips
                if len(sent_clips["sent"]) > 100:
                    sent_clips["sent"] = sent_clips["sent"][-100:]

                save_json(SENT_CLIPS_FILE, sent_clips)
                return f"https://www.youtube.com/watch?v={video_id}"
        
        attempts += 1

    return None
    
#Send the clip every 24 hours
@tasks.loop(hours=24)
async def daily_daredevil_clip():
    for guild_id, channel_id in channel_map.items():
        channel = bot.get_channel(channel_id)
        if channel:
            video_url = get_random_daredevil_clip()
            if not video_url:
                await channel.send("❌ Couldn't fetch a valid Daredevil clip today.")
                return
            message = await channel.send(f"**Daily Daredevil Clip:** {video_url}\nReact with 🌟 to favorite, ❌ to block from being shown again!")
            await message.add_reaction("🌟")
            await message.add_reaction("❌")


# === Bot Events === #
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    message = reaction.message
    if not (
        message.content.startswith("**Daily Daredevil Clip:**") or
        message.content.startswith("**Here's a Daredevil clip:**")
    ):
        return

    # Extract the URL using a regex pattern
    url_pattern = r"(https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+)"
    match = re.search(url_pattern, message.content)

    if not match:
        return  # If no URL is found, don't proceed

    video_url = match.group(0)  # This gets the YouTube URL
    video_id = video_url.split("v=")[-1]  # Extract video ID from URL

    if reaction.emoji == "🌟":
        # Save the clip for user
        if str(user.id) not in favorite_clips:
            favorite_clips[str(user.id)] = []
        if video_url not in favorite_clips[str(user.id)]:
            favorite_clips[str(user.id)].append(video_url)
        save_json(FAVORITE_CLIPS_FILE, favorite_clips)
        await message.channel.send(f"✅ {user.mention} added this clip to favorites, +10% chance to appear again!")

    elif reaction.emoji == "❌":
        # Block clip permanently
        if video_id not in blocked_clips["blocked"]:
            blocked_clips["blocked"].append(video_id)
            save_json(BLOCKED_CLIPS_FILE, blocked_clips)
        await message.delete()
        await message.channel.send(f"🚫 {user.mention} blocked this clip from being shown again!")

# when bot joins server
@bot.event
async def on_guild_join(guild):
    owner = guild.owner
    if owner:
        try:
            await owner.send(f"👋 Thanks for adding me to **{guild.name}**! Use `!setchannel` in your desired text channel to receive daily Daredevil clips.")
        except:
            pass

# set channel for clips
@bot.command()
@commands.has_permissions(manage_guild=True)
async def setchannel(ctx):
    guild_id = str(ctx.guild.id)
    channel_map[guild_id] = ctx.channel.id
    save_json(CHANNEL_MAP_FILE, channel_map)
    await ctx.send(f"✅ This channel has been set to receive daily Daredevil clips!")

# Manual Fetching Clip
# Get random clip with !daredevil
@bot.command()
async def daredevil(ctx):
    video_url = get_random_daredevil_clip()
    if not video_url:
        await ctx.send("❌ Couldn't find a valid clip.")
        return
    message = await ctx.send(f"**Here's a Daredevil clip:** {video_url}\nReact with 🌟 to favorite, ❌ to block from being shown again!")
    await message.add_reaction("🌟")
    await message.add_reaction("❌")

# Show user favorite clips with !saved
@bot.command()
async def saved(ctx):
    user_id = str(ctx.author.id)
    if user_id in favorite_clips and favorite_clips[user_id]:
        await ctx.send(f"📂 **Your saved Daredevil clips:**\n" + "\n".join(favorite_clips[user_id]))
    else:
        await ctx.send("⚠️ You haven't saved any clips yet!")

# Start the Bot
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    daily_daredevil_clip.start()

bot.run(TOKEN)