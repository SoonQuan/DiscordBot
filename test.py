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


class Test(commands.Cog):
  """ Basic bot commands """
  def __init__(self,client):
    self.client = client

  @commands.command()
  async def test(self,ctx):
    """ Check the latency of the bot """
    
    channel = self.client.get_channel(703054964200833125)
    role = channel.guild.get_role(832076962713305098)
    prefix = get_prefix(client,channel)

    await channel.send(prefix)



def setup(client):
  client.add_cog(Test(client))