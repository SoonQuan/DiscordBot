import discord
from discord.ext import commands
import os
import pymongo
from pymongo import MongoClient

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]


def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
botcolour = 0x0fa4aab


class Greetings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
      if member.guild.id == 825583328111230977:
        channel = member.guild.system_channel
        if channel is not None:
          msg = f"Welcome to {member.guild} {member.mention}\nYou are going to be a lab rat :rat:"
          return await channel.send(msg)
      elif member.guild.id == 692808940190433360:
        channel = member.guild.system_channel
        if channel is not None:
          msg = f"Welcome to Null Community {member.mention}\nYou can post your application here <#694708991321833492>\nRequest for role here <#697647239123959857>\nCombat class role here <#806087564867928094>"
          return await channel.send(msg)

def setup(client):
  client.add_cog(Greetings(client))