import os, discord, random
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import re


cluster = MongoClient(os.getenv('MONGODB'))
gptapikey = os.getenv('GPTAPIKEY')
db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]
liveness = db["liveness"]
mon = liveness.find_one({"setting":"main"})


def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
botcolour = 0x0fa4aab

def regexCheck(text):
    pattern = "\[.*\]\(.*\)"
    return re.search(pattern, text, re.MULTILINE)

class Modd(commands.Cog):
  """ Mod commands """
  def __init__(self,client):
    self.client = client

  @commands.Cog.listener()
  async def on_message(self,msg):
    if msg.author.id == self.client.user.id:
      return
    if msg.guild.id == 818068910581874719 and regexCheck(str(msg.content)) and msg.author.bot != True:
      webhook = await msg.channel.create_webhook(name=msg.author.name)
      message = str(msg.content)[1:-1].replace("](", "\n||")+"||"
      await msg.delete()
      await webhook.send(message, username=msg.author.name, avatar_url=msg.author.avatar_url)

def setup(client):
  client.add_cog(Modd(client))
