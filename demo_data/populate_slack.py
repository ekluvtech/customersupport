"""Script to populate Slack with sample messages for demo purposes"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def populate_slack():
    """Populate Slack with sample messages"""
    
    # Check for credentials
    if not os.getenv("SLACK_TOKEN"):
        print("Error: Slack token not found in environment variables.")
        print("Please set: SLACK_TOKEN")
        print()
        print("Note: This script requires the slack-sdk library.")
        print("Install it with: pip install slack-sdk")
        return
    
    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
    except ImportError:
        print("Error: slack-sdk library not installed.")
        print("Install it with: pip install slack-sdk")
        return
    
    # Load sample data
    data_file = Path(__file__).parent / "sample_data.json"
    with open(data_file, "r") as f:
        data = json.load(f)
    
    # Initialize Slack client
    client = WebClient(token=os.getenv("SLACK_TOKEN"))
    
    print("=" * 60)
    print("Populating Slack with Sample Messages")
    print("=" * 60)
    print()
    
    # Get or create channels
    channels = {}
    channel_names = set()
    
    for message in data["slack_messages"]:
        channel_names.add(message["channel"])
    
    # List existing channels
    try:
        result = client.conversations_list(types="public_channel,private_channel")
        existing_channels = {ch["name"]: ch["id"] for ch in result["channels"]}
    except SlackApiError as e:
        print(f"Error listing channels: {e}")
        return
    
    # Get or create channels
    for channel_name in channel_names:
        if channel_name in existing_channels:
            channels[channel_name] = existing_channels[channel_name]
            print(f"Using existing channel: #{channel_name}")
        else:
            # Try to create channel (may fail if permissions insufficient)
            try:
                result = client.conversations_create(name=channel_name)
                channels[channel_name] = result["channel"]["id"]
                print(f"Created channel: #{channel_name}")
            except SlackApiError as e:
                if e.response["error"] == "name_taken":
                    # Channel exists but wasn't in list (might be private)
                    print(f"Channel #{channel_name} exists but is not accessible")
                else:
                    print(f"Error creating channel #{channel_name}: {e}")
                continue
    
    # Get user list to map emails to user IDs
    user_map = {}
    try:
        result = client.users_list()
        for user in result["members"]:
            if user.get("profile", {}).get("email"):
                user_map[user["profile"]["email"]] = user["id"]
    except SlackApiError as e:
        print(f"Warning: Could not get user list: {e}")
    
    # Group messages by channel and send them
    messages_by_channel = {}
    for message in data["slack_messages"]:
        channel = message["channel"]
        if channel not in messages_by_channel:
            messages_by_channel[channel] = []
        messages_by_channel[channel].append(message)
    
    sent_messages = []
    
    for channel_name, messages in messages_by_channel.items():
        if channel_name not in channels:
            print(f"Skipping channel #{channel_name} - not accessible")
            continue
        
        channel_id = channels[channel_name]
        print(f"\nSending messages to #{channel_name}...")
        
        for message in sorted(messages, key=lambda x: x.get("timestamp", "")):
            try:
                text = message["text"]
                user_email = message.get("user", "")
                
                # Try to find user ID, otherwise use default user
                user_id = user_map.get(user_email)
                
                if user_id:
                    # Send message as the user (requires special permissions)
                    # For demo, we'll just send as the bot
                    result = client.chat_postMessage(
                        channel=channel_id,
                        text=f"*{user_email}*: {text}"
                    )
                else:
                    # Send as bot with user email in text
                    result = client.chat_postMessage(
                        channel=channel_id,
                        text=f"*{user_email}*: {text}"
                    )
                
                sent_messages.append({
                    "channel": channel_name,
                    "text": text,
                    "ts": result["ts"]
                })
                
                print(f"  ✓ Sent message from {user_email}")
                
            except SlackApiError as e:
                print(f"  ✗ Error sending message: {e}")
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Successfully sent {len(sent_messages)} messages to {len(channels)} channels")
    print()
    print("Note: Messages are sent as the bot account.")
    print("For realistic demo, you may want to use Slack's chat.scheduleMessage API")
    print("or manually post messages from different user accounts.")


if __name__ == "__main__":
    populate_slack()

