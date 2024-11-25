from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import pandas as pd
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv(".env")

# Environment variables for Telegram credentials
api_hash = os.getenv("api_hash")
api_id = os.getenv("api_id")
username = os.getenv("tele_name")
phone_number = os.getenv("tele_phonenumber")

# Create the client
client = TelegramClient(username, api_id, api_hash)

async def get_latest_posts(channel_name, topk=10):
    """
    Retrieves the top 'topk' latest posts from a specific Telegram channel.

    Args:
        channel_name (str): The Telegram channel username (e.g., '@examplechannel').
        topk (int): The number of latest posts to retrieve.

    Returns:
        pd.DataFrame: A DataFrame containing the top 'topk' latest posts with columns
                      'channel_name', 'post_id', 'content', 'date'.
    """
    await client.start(phone=phone_number)
    try:
        # Get the channel entity
        print(f"Fetching latest posts from channel: {channel_name}")
        channel = await client.get_entity(channel_name)
        
        # Fetch messages
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=topk,
            max_id=0,
            min_id=0,
            hash=0
        ))

        # Collect posts
        posts = []
        for msg in history.messages[:topk]:
            if msg.message:
                posts.append([channel_name, msg.id, msg.message, msg.date])
        
        # Convert to DataFrame
        posts_df = pd.DataFrame(posts, columns=["channel_name", "post_id", "content", "date"])
        print(f"Successfully retrieved {len(posts)} posts from {channel_name}")
        return posts_df

    except Exception as e:
        print(f"Error retrieving posts from {channel_name}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error
    finally:
        await client.disconnect()

# Example usage
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    channel_name = '@FinancialStreetVN'
    topk_posts = loop.run_until_complete(get_latest_posts(channel_name, topk=10))
    if not topk_posts.empty:
        print(topk_posts)
    else:
        print(f"No posts found or an error occurred for {channel_name}")
