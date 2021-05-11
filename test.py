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

class Test(commands.Cog):
  """ Basic bot commands """
  def __init__(self,client):
    self.client = client

  @commands.command()
  async def hello(self,ctx, title,*,msg):
    """ Check the colour of the bot """
    user = ctx.author
    with open("notes.json", "r") as f:
      notes = json.load(f)
    note = str(msg)
    notes[user.guild.id][title] = note

    with open("notes.json","w") as f:
        json.dump(notes,f)
    em = discord.Embed(description="Note saved", colour = botcolour)
    await ctx.send(embed = em)






def setup(client):
  client.add_cog(Test(client))