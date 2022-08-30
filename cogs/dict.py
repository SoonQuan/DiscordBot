import os
import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
from google_translate_py import AsyncTranslator
import googletrans

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]

my_secret = str(os.getenv('UBKEY'))

print(my_secret)
def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
botcolour = 0x0fa4aab

import requests
import datetime

class Dictionary(commands.Cog):
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

  @commands.command(aliases = ['trans'])
  async def translate(self,ctx, lang="en", *, args):
    """ Translate your message into the language you want """
    if lang not in googletrans.LANGUAGES and lang not in googletrans.LANGCODES:
      em = discord.Embed(title='Look for langauge code here',
                        url='https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes',
                        description= f"For example: !translate <code> <words to translate>",
                        color=discord.Color.red())
      return await ctx.send(embed = em)
    try:
      translate_text = await AsyncTranslator().translate(args, "", lang)
      em = discord.Embed(description = translate_text, color=ctx.author.color)
      return await ctx.send(embed = em)
    except:
      em = discord.Embed(description = "error in translation", color=ctx.author.color)
      return await ctx.send(embed = em)

  # @commands.command(aliases = ['ptrans'])
  # async def ptranslate(self,ctx, lang="en", *,args="translate <code> <words to translate and pronounce>"):
  #   """ Translate your message into the language you want """
  #   if lang.lower() not in LANGUAGES:
  #     em = discord.Embed(title='Look for langauge code here',
  #                       url='https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes',
  #                       description= f"For example: !translate <code> <words to translate>",
  #                       color=discord.Color.red())
  #     return await ctx.send(embed = em)        
  #   else:
  #     t = google_translator()
  #     a = t.translate(args, lang_tgt=lang,pronounce=True)
  #     em = discord.Embed(description = f'Translated: {a[0]}\nPronouce: {a[2]}', color=ctx.author.color)
  #     return await ctx.send(embed = em)
    


def setup(client):
  client.add_cog(Dictionary(client))