import discord
from discord.ext import commands
import os
import pymongo
from pymongo import MongoClient
import asyncio

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]


def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
botcolour = 0x0fa4aab

import json




"""

Bank Heist
|
----- Cost
      |
      ----- Spend 2k currency to join heist
|
----- Win rates
      |
      ----- More people equal higher chance
      ----- Min 2 Max 10
      ----- People | Rates = (people/10)**2
            |
            ----- 2 , 4%
            ----- 3 , 9%
            ----- 5 , 25%
            ----- 10 , 100%
      |
      ----- When win: each player that join has a 40% chance to die
      ----- Lose the gains and entry cost
      |
      ----- gain is split among the group [DONE]
|
----- Start session
      |
      ----- Join
      |
      ----- Exit

    with open("notes.json","w") as f:
        json.dump(notes,f,indent=4)
"""


import random
import yfinance as yf

class Test(commands.Cog):
  """ Basic bot commands """
  def __init__(self,client):
    self.client = client

  @commands.command()
  async def event(self,ctx, event):
    """ Check the colour of the bot """
    with open("heist.json", "r") as f:
      events = json.load(f)
    event1 = event.capitalize()
    choice = random.choice(events[event1])
    quote = choice[0]
    await ctx.send(f"Events: {quote.format(ctx.author.name)}\nOutcome: {choice[1]}")

    

def setup(client):
  client.add_cog(Test(client))