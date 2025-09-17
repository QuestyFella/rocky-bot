import discord
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv('.env')

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID",0))
FORMURL=os.getenv("FORM_URL")
FIELDS = {
    "Reason": "entry.987654321",
    "Amount": "entry.876543210",
    "Deadline": "entry.765432109",
    "Note": "entry.654321098",
}

intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)

def parse_message(content):
    pattern = r"(?i)^Reason:\s*(.*?)\s*^Amount:\s*(.*?)\s*^Deadline:\s*(.*?)\s*^Note:\s*(.*)"
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    if not match:
        return None
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
    print(f"Bot connected as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot or message.channel.id != CHANNEL_ID:
        return

    data = parse_message(message.content)
    if not data:
        await message.channel.send("❌ Invalid format. Use:\n```\nReason: ...\nAmount: ...\nDeadline: ...\nNote: ...\n```")
        return

    success = send_to_google_form(data)
    if success:
        await message.channel.send("Request submitted successfully.")
    else:
        await message.channel.send("❌ Failed to submit the request. Try again later.")

if TOKEN is None:
    print("No token found. Please set the DISCORD_TOKEN environment variable.")
elif TOKEN is not None:
    client.run(TOKEN)
