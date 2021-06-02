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

  @commands.command(aliases = ['t?','tread'])
  async def test_read_note(self,ctx,title="listing"):
    """ Refer to the reference """
    user = ctx.author
    with open("notes.json", "r") as f:
      notes = json.load(f)
    nlist = list(notes[str(user.guild.id)])
    d = {}
    out = []
    if title == "listing":
      n = 3
      final = [nlist[i * n:(i + 1) * n] for i in range((len(nlist) + n - 1) // n )]
      for i in range(len(final)):
        d["Page{0}".format(i+1)] = "\n".join(final[i])
      for page in list(d.keys()):
        out.append(discord.Embed(title="List Contain:",description=d[page], color=ctx.author.color))
      print(out)
      paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
      paginator.add_reaction('⏮️', "first")
      paginator.add_reaction('⏪', "back")
      paginator.add_reaction('🔐', "lock")
      paginator.add_reaction('⏩', "next")
      paginator.add_reaction('⏭️', "last")
      embeds = out
      return await paginator.run(embeds)
    try:
      msg = notes[str(user.guild.id)][str(title)]
      em = discord.Embed(description=msg, colour = botcolour)
      return await ctx.send(embed = em)
    except:
      msg = f'There is no note on `{str(title)}`'
      em = discord.Embed(description=msg, colour = discord.Color.red())
      return await ctx.send(embed = em)



def setup(client):
  client.add_cog(Test(client))