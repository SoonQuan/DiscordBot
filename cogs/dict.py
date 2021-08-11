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

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
botcolour = 0x0fa4aab

import requests
import datetime

class dictionary(commands.Cog):
  """ Dictionary commands """
  def __init__(self,client):
    self.client = client

  @commands.command(aliases=["urban", "ud"])
  async def urbandictionary(self, ctx,*, term):
    """ Search Urban Dictionary """
    url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"

    querystring = {"term":term}

    headers = {
        'x-rapidapi-key': "a5280e4443msh0945d0f966eba91p15efdfjsnf7aae3d323ef",
        'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring).json()
    text = response["list"][0]["definition"]
    info = (text[:4000] + '..') if len(text) > 4000 else text
    info = '. '.join(i.capitalize() for i in info.split('. '))
    url = response["list"][0]['permalink']
    em = discord.Embed(title=term.capitalize(), description=info, color=discord.Color.orange(), url=url, timestamp=datetime.datetime.utcnow())
    em.set_footer(text="Credits to Urban Dictionary", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=em)


def setup(client):
  client.add_cog(dictionary(client))