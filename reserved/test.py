import discord
from discord.ext import commands
import os
import pymongo
from pymongo import MongoClient
import asyncio
import DiscordUtils

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]


def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
botcolour = 0x0fa4aab

import json
from datetime import datetime,timezone
from dateutil import parser, tz
import pytz


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
import random


class Test(commands.Cog):
  """ Basic bot commands """
  def __init__(self,client):
    self.client = client

  @commands.command()
  async def test(self,ctx):
    """ Calculate damage """
    def check(m):
      return m.author == ctx.author and m.channel == ctx.message.channel
    
    em = discord.Embed(description = f'When is your `Attack`?', colour = ctx.author.color)
    await ctx.send(embed = em)
    try:
      msg1 = await self.client.wait_for("message",timeout= 60, check=check)
      attack = msg1.content
      em = discord.Embed(description = f'When is your `Attack`?', colour = ctx.author.color)
      await ctx.send(embed = em)
      try:
        msg2 = await self.client.wait_for("message",timeout= 60, check=check)
        event_end = msg2.content
        notes[str(event_name)]['END'] = event_end
        with open("event.json","w") as f:
            json.dump(notes,f,indent=4)
        em = discord.Embed(description=f"Event on {str(event_name)} recorded", colour = botcolour)
        return await ctx.send(embed = em)        
      except asyncio.TimeoutError:
        em = discord.Embed(description = f"You took too long... try again later when you are ready", colour = discord.Color.red())
        return await ctx.send(embed = em)
    except asyncio.TimeoutError:
      em = discord.Embed(description = f"You took too long... try again later when you are ready", colour = discord.Color.red())
      return await ctx.send(embed = em)




def setup(client):
  client.add_cog(Test(client))