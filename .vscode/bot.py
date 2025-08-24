import discord
import re
import requests

class MyClient(discord.Client):
    async def connect(self):
        print(f'Logged on as{self.user}!')
        
    async def user(self):
         
