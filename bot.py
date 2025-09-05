import discord
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv('.env')

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID",0))
FORMURL=os.getenv("FORM_URL")