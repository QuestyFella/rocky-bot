import discord
import os
import re
import requests
import json
from dotenv import load_dotenv

load_dotenv('.env')

TOKEN = os.getenv("DISCORD_TOKEN")
FORMURL=os.getenv("FORM_URL")
FIELDS = {
    "Reason": "entry.987654321",
    "Amount": "entry.876543210",
    "Deadline": "entry.765432109",
    "Note": "entry.654321098",
}

# File to store the channel ID
CHANNEL_ID_FILE = "channel_id.json"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Required for reading message content

client = discord.Client(intents=intents)

# Global variable to store the channel ID
target_channel_id = None

def save_channel_id(channel_id):
    """Save the channel ID to a file"""
    with open(CHANNEL_ID_FILE, 'w') as f:
        json.dump({"channel_id": channel_id}, f)

def load_channel_id():
    # loads channel id from a file since I cant be arsed to reset it if it ever goes down
    global target_channel_id
    try:
        with open(CHANNEL_ID_FILE, 'r') as f:
            data = json.load(f)
            target_channel_id = data.get("channel_id")
    except FileNotFoundError:
        # File doesn't exist yet, that's okay
        pass
    except json.JSONDecodeError:
        # File is corrupted, reset it
        save_channel_id(None)

def parse_message(content):
    # Case-insensitive matching for field names using regex
    pattern = r"(?i)^Reason:\s*(.*?)\s*^Amount:\s*(.*?)\s*^Deadline:\s*(.*?)\s*^Note:\s*(.*)"
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    
    if not match:
        # Try to identify what might be wrong with the message
        lines = content.strip().split('\
')
        if len(lines) < 4:
            return {"error": "Message must contain at least 4 lines for Reason, Amount, Deadline, and Note."}
            
        # Check for case-insensitive field presence
        content_lower = content.lower()
        required_fields = ["reason", "amount", "deadline", "note"]
        missing_fields = [field for field in required_fields if field not in content_lower]
        
        if missing_fields:
            return {"error": f"Missing required fields: {', '.join(missing_fields)}"}
            
        return {"error": "Invalid format. Fields must be in the correct order."}
        
    reason, amount, deadline, note = match.groups()
    return {
        "Reason": reason.strip(),
        "Amount": amount.strip(),
        "Deadline": deadline.strip(),
        "Note": note.strip(),
    }

def send_to_google_form(data):
    payload = {FIELDS[key]: value for key, value in data.items()}
    if FORMURL is None:
        print("No form URL found. Please set the FORMURL environment variable.")
        return False
    response = requests.post(FORMURL, data=payload)
    return response.status_code == 200

@client.event
async def on_ready():
    # Load the channel ID from file
    load_channel_id()
    print(f"Bot connected as {client.user}")
    if target_channel_id:
        channel = client.get_channel(target_channel_id)
        if channel:
            print(f"Listening for messages in {channel.name} (ID: {target_channel_id})")
        else:
            print(f"Warning: Channel with ID {target_channel_id} not found!")

@client.event
async def on_message(message):
    # Handle the set_channel command
    if message.content.startswith('!set_channel'):
        # Check if the user has administrator permissions
        if not message.author.guild_permissions.administrator:
            await message.channel.send("❌ You need administrator permissions to set the channel.")
            return
            
        # Set the channel to the current channel
        global target_channel_id
        target_channel_id = message.channel.id
        save_channel_id(target_channel_id)
        await message.channel.send(f"✅ Channel set to {message.channel.mention} (ID: {message.channel.id})")
        return
    
    # Ignore bot messages and messages not from the target channel
    if message.author.bot:
        return
        
    # If no target channel is set, ignore all messages
    if target_channel_id is None:
        return
        
    # If target channel is set, only process messages from that channel
    if message.channel.id != target_channel_id:
        return

    data = parse_message(message.content)
    if "error" in data:
        await message.channel.send(f"❌ {data['error']}\
Use:\
```\
Reason: ...\
Amount: ...\
Deadline: ...\
Note: ...\
```")
        return
        
    # Remove 'error' key if it exists but is None (shouldn't happen with new logic)
    data.pop("error", None)

    success = send_to_google_form(data)
    if success:
        await message.channel.send("Request submitted successfully.")
    else:
        await message.channel.send("❌ Failed to submit the request. Try again later.")

if TOKEN is None:
    print("No token found. Please set the DISCORD_TOKEN environment variable.")
elif TOKEN is not None:
    client.run(TOKEN)
