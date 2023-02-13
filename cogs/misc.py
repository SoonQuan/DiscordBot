import os, discord, random
from discord.ext import commands
import pymongo
from pymongo import MongoClient

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

class Misc(commands.Cog):
  """ GPT commands """
  def __init__(self,client):
    self.client = client

  @commands.command()
  async def dig(self, ctx, size=5):
    if size > 7:
      size = 7
    elif size < 1:
      size = 1
    elif type(size) != int:
      size = 5
    temp = ["||<a:helloo:835770495865454602>||"]
    blank = "||<:fuckingpng:834386099492093962>||"
    outlist=[]
    output = ""
    for _ in range(1,size**2):
      temp.append(blank)
    random.shuffle(temp)
    while temp != []:
      outlist.append(temp[:size])
      temp = temp[size:]
    for n in range(len(outlist)):
      output += " ".join(outlist[n])
      if n != size-1:
        output += "\n"
    embed = discord.Embed(description=output, colour = ctx.author.color)
    return await ctx.reply(embed=embed)

def setup(client):
  client.add_cog(Misc(client))
