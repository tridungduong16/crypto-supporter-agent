from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerChannel
import asyncio

# Initial imports
from datetime import datetime, timezone
import pandas as pd
import time
import json
import re
from dotenv import load_dotenv
import os
from telethon.sync import TelegramClient
# from google.colab import files
import asyncio
from tqdm import tqdm

# Load environment variables
load_dotenv(".env")

# Environment variables for Telegram credentials
api_hash = os.getenv("api_hash")
api_id = os.getenv("api_id")
username = os.getenv("tele_name")
phone_number = os.getenv("tele_phonenumber")


channels = [
    '@FinancialStreetVN',
    '@Jesstraining',
    '@ThuanCapital',
    '@binance_announcements',
    '@ChungkhoanGalaxy'
]

# Create the client
client = TelegramClient(username, api_id, api_hash)

async def get_channel_posts():
    await client.start(phone=phone_number)
    # DataFrame to store all posts
    output_folder = "/workspaces/ai-agent/dataset/telegram_posts"
    for channel_username in (channels):    
        print(f"Channel name: {channel_username}")
        channel = await client.get_entity(channel_username)
        file_path = os.path.join(output_folder, f"{channel_username.strip('@')}.csv")
        if os.path.exists(file_path):
            print(f"File already exists for {channel_username}. Skipping...")
            continue
        offset_id = 0
        limit = 100  # Number of posts to fetch in each request
        all_posts = []
        while True:
            history = await client(GetHistoryRequest(
                peer=channel,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                break
            posts = [msg for msg in (history.messages) if msg.post]
            for i in posts:
                print(i.message)
            # print(posts)
            all_posts.extend(posts)
            offset_id = history.messages[-1].id
        
        all_posts_df = []
        for post in tqdm(all_posts):
            if post.message:
                all_posts_df.append([channel_username, post.id, post.message, post.date])
        all_posts_df = pd.DataFrame(all_posts_df, columns=["channel_name", "post_id", "content", "date"])
        all_posts_df.to_csv(file_path, index=False)
    await client.disconnect()
loop = asyncio.get_event_loop()
loop.run_until_complete(get_channel_posts())
