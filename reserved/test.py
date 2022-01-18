import discord
from discord.ext import commands
import os
import pymongo
from pymongo import MongoClient
import asyncio
import DiscordUtils

from datetime import datetime
from pytz import timezone

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]
timezones = db["timezone"]


def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
botcolour = 0x0fa4aab


"""
    print('datetime.now(pytz.timezone("US/Pacific")): ', datetime.now(pytz.timezone("US/Pacific")))


    with open("notes.json","w") as f:
        json.dump(notes,f,indent=4)
        
The dmg formula is:

[(Atk x Card %) x (Crit Damage - CritDef) - Def] x Element + [(Atk x Pierce#) - (Def x Resistance)]

Crit Damage# - if it crits

Pierce # - if you have multiplier like x3 you apply it here as well

Element: Multiply with 1, 0.8 or 1.3 based on type advantage, disadvantage or neutral

Damage from Freeze cards get applied after this initial calculation, so take the value which results from the formula and apply 80% or 200% to it then add it to the initial value
        
"""
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import re
class Test(commands.Cog):
  """ Basic bot commands """
  def __init__(self,client):
    self.client = client


  @commands.command()
  async def test(self, ctx, *,msg):
    result = re.search(r"\[([A-Za-z0-9_]+)\]", msg)
    print(result.group(1))

def setup(client):
  client.add_cog(Test(client))