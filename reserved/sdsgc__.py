import discord
from discord.ext import commands
import os
import pymongo
from pymongo import MongoClient
import json
from datetime import datetime
from dateutil import parser, tz
import asyncio

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


class SDSGC(commands.Cog):
  def __init__(self, client):
      self.client = client



def setup(client):
  client.add_cog(SDSGC(client))