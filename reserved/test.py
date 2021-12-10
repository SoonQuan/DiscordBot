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
import datetime
from google_translate_py import AsyncTranslator
import googletrans
import requests
import math

class Test(commands.Cog):
  """ Basic bot commands """
  def __init__(self,client):
    self.client = client

  @commands.command()
  async def est(self,ctx, lang_to, *,args):
    """ Translate your message into the language you want """
    lang_to = lang_to.lower()
    if lang_to not in googletrans.LANGUAGES and lang_to not in googletrans.LANGCODES:
      raise commands.BadArgument("invalid language to translate text to")
    translate_text = await AsyncTranslator().translate(args, "", lang_to)
    await ctx.send(translate_text)
    # if lang.lower() not in LANGUAGES:
    #   em = discord.Embed(title='Look for langauge code here',
    #                     url='https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes',
    #                     description= f"For example: !translate <code> <words to translate>",
    #                     color=discord.Color.red())
    #   return await ctx.send(embed = em)        
    # else:
    #   t = google_translator()
    #   a = t.translate(args, lang_tgt=lang)
    #   em = discord.Embed(description = a, color=ctx.author.color)
    #   return await ctx.send(embed = em)

  @commands.command(aliases=["tes", "te"])
  async def test(self, ctx, *, participants=''):

    if participants == '':
      em = discord.Embed(title='Please provide participants',colour = botcolour)
      await ctx.send(embed=em)
    em = discord.Embed(title='Participant',colour = botcolour)
    await ctx.send(embed=em)

  @commands.command()
  async def tt(self, ctx, a=2):

    await ctx.send(generate_tournament(a))

def tournament_round( no_of_teams , matchlist ):
    new_matches = []
    for team_or_match in matchlist:
        if type(team_or_match) == type([]):
            new_matches += [ tournament_round( no_of_teams, team_or_match ) ]
        else:
            new_matches += [ [ team_or_match, no_of_teams + 1 - team_or_match ] ]
    return new_matches

def flatten_list( matches ):
    teamlist = []
    for team_or_match in matches:
        if type(team_or_match) == type([]):
            teamlist += flatten_list( team_or_match )
        else:
            teamlist += [team_or_match]
    return teamlist

def generate_tournament( num ):
    num_rounds = math.log( num, 2 )
    if num_rounds != math.trunc( num_rounds ):
        raise ValueError( "Number of teams must be a power of 2" )
    teams = 1
    result = [1]
    while teams != num:
        teams *= 2
        result = tournament_round( teams, result )
    return flatten_list( result )

def setup(client):
  client.add_cog(Test(client))