import asyncio
import pandas as pd
from telethon.sync import TelegramClient

# --- Configuration ---
# Replace these with your actual credentials and the channel you want to analyze
API_ID = 25295686  # YOUR_API_ID - Replace with your integer API ID
API_HASH = '19c4a8cb9db5acb8580d86f056e86693'  # Replace with your API hash string
PHONE_NUMBER = '+251900045008'  # Replace with your international phone number
CHANNEL_USERNAME = 'Dagmawi_Babi'  # Replace with the public channel's username (without '@')
SESSION_NAME = 'telegram_session' # Name for the session file that will be created

# --- Main Analysis Function ---
async def analyze_channel():
    """
    Connects to Telegram, fetches messages from a channel, analyzes them,
    and prints the results.
    """
    # Use 'async with' to automatically connect and disconnect
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        print(f"Successfully connected. Starting analysis for @{CHANNEL_USERNAME}...")

        # Create a list to hold all the post data
        all_posts_data = []

        # Use client.iter_messages() to get all messages from the channel.
        # You can add a `limit` argument to get a specific number of recent posts,
        # e.g., limit=100 for the last 100 posts.
        # Leaving it empty will attempt to fetch all messages.
        async for message in client.iter_messages(CHANNEL_USERNAME, limit=100): # Increased limit for better demo
            if message is None:
                continue

            # 1. View Count
            view_count = message.views if message.views else 0

            # 2. Engagement: Forwards, Comments, Reactions
            forward_count = message.forwards if message.forwards else 0

            comment_count = 0
            if message.replies:
                comment_count = message.replies.replies

            reactions_summary = {}
            if message.reactions:
                for reaction in message.reactions.results:
                    emoji = reaction.reaction.emoticon
                    count = reaction.count
                    reactions_summary[emoji] = count

            # 3. Post Type
            post_type = []
            if message.text:
                post_type.append('Text')
            if message.photo:
                post_type.append('Photo')
            if message.video:
                post_type.append('Video')
            if message.document:
                # This can be any file, like a GIF, audio, or general document
                post_type.append('Document/File')
            if message.web_preview:
                post_type.append('Link')
            
            if not post_type:
                post_type.append('Other') # For polls, location, etc.

            # 4. Post Size
            char_count = len(message.text) if message.text else 0
            
            file_size_mb = 0
            if message.media and hasattr(message.media, 'document') and hasattr(message.media.document, 'size'):
                # General case for documents, videos, etc.
                file_size_mb = round(message.media.document.size / (1024 * 1024), 2)
            elif message.photo:
                # Photos have multiple sizes, get the largest one
                largest_photo = message.photo.sizes[-1]
                if hasattr(largest_photo, 'size'):
                     file_size_mb = round(largest_photo.size / (1024 * 1024), 2)


            # Store all collected data in a dictionary
            post_data = {
                "Post ID": message.id,
                "Date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                "Views": view_count,
                "Forwards": forward_count,
                "Comments": comment_count,
                "Reactions": reactions_summary if reactions_summary else "None",
                "Post Type": ', '.join(post_type),
                "Character Count": char_count,
                "File Size (MB)": file_size_mb,
                "Message Text": message.text.replace('\n', ' ')[:100] + '...' if message.text else "N/A" # Truncate long texts
            }
            
            all_posts_data.append(post_data)

            # --- Print the detailed analysis for the current post ---
            print("-" * 50)
            print(f"Analyzing Post ID: {post_data['Post ID']} | Date: {post_data['Date']}")
            print(f"  - Views: {post_data['Views']}")
            print(f"  - Forwards: {post_data['Forwards']}")
            print(f"  - Comments: {post_data['Comments']}")
            print(f"  - Reactions: {post_data['Reactions']}")
            print(f"  - Type: {post_data['Post Type']}")
            print(f"  - Text Length: {post_data['Character Count']} characters")
            print(f"  - Attachment Size: {post_data['File Size (MB)']} MB")
            print(f"  - Text Preview: {post_data['Message Text']}")
            print("-" * 50 + "\n")

        print(f"Analysis complete. Fetched data for {len(all_posts_data)} posts.")
        
        # --- (Optional) Save the data to a CSV file for further analysis ---
        if all_posts_data:
            df = pd.DataFrame(all_posts_data)
            output_filename = f"{CHANNEL_USERNAME}_channel_analysis.csv"
            df.to_csv(output_filename, index=False)
            print(f"\nAll data has been saved to '{output_filename}'")


if __name__ == "__main__":
    # In some environments (like Jupyter notebooks), you might need to use
    # asyncio.get_event_loop().run_until_complete(analyze_channel())
    # For a standard .py script, asyncio.run() is preferred.
    asyncio.run(analyze_channel())