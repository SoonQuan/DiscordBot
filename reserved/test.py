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

import json
from datetime import datetime,timezone
from dateutil import parser, tz
import pytz


"""
    print('datetime.now(pytz.timezone("US/Pacific")): ', datetime.now(pytz.timezone("US/Pacific")))


    with open("notes.json","w") as f:
        json.dump(notes,f,indent=4)

        
"""
import random


class Test(commands.Cog):
  """ Basic bot commands """
  def __init__(self,client):
    self.client = client

  @commands.command(aliases = ['+e'])
  async def add_event(self,ctx,*,event):
    """ Add an event """
    def check(m):
      return m.author == ctx.author and m.channel == ctx.message.channel
    with open("event.json", "r") as f:
      notes = json.load(f)
    event_name = str(event)
    if str(event_name) not in notes:
      notes[str(event_name)] = {}
    em = discord.Embed(description = f'When does `{event_name}` START?', colour = ctx.author.color)
    await ctx.send(embed = em)
    try:
      msg1 = await self.client.wait_for("message",timeout= 60, check=check)
      event_start = msg1.content
      notes[str(event_name)]['START'] = event_start
      em = discord.Embed(description = f'When does `{event_name}` END?', colour = ctx.author.color)
      await ctx.send(embed = em)
      try:
        msg2 = await self.client.wait_for("message",timeout= 60, check=check)
        event_end = msg2.content
        notes[str(event_name)]['END'] = event_end
        with open("event.json","w") as f:
            json.dump(notes,f,indent=4)
        em = discord.Embed(description=f"Event on {str(event_name)} recorded", colour = botcolour)
        return await ctx.send(embed = em)        
      except asyncio.TimeoutError:
        em = discord.Embed(description = f"You took too long... try again later when you are ready", colour = discord.Color.red())
        return await ctx.send(embed = em)
    except asyncio.TimeoutError:
      em = discord.Embed(description = f"You took too long... try again later when you are ready", colour = discord.Color.red())
      return await ctx.send(embed = em)

  @commands.command()
  async def timenow(self,ctx):
    await ctx.send(datetime.now(pytz.timezone("US/Pacific")))

  @commands.command()
  async def test(self,ctx):
    def strfdelta(tdelta, fmt):
      d = {"days": tdelta.days}
      d["hours"], rem = divmod(tdelta.seconds, 3600)
      d["minutes"], d["seconds"] = divmod(rem, 60)
      return fmt.format(**d)

    with open("event.json", "r") as f:
      main = json.load(f)
    events = dict(main)
    # start_date = parser.parse('6/16 12 AM')
    # end_date = parser.parse('6/21 11:59 PM')
    # start_date = start_date.replace(tzinfo=tz.gettz("US/Pacific"))
    # end_date = end_date.replace(tzinfo=tz.gettz("US/Pacific"))
    now = datetime.now(tz=tz.gettz("US/Pacific"))
    ongoing = "```diff\n"
    upcoming = "```diff\n"
    for event in events:
      start_date = parser.parse(events[event]["START"])
      end_date = parser.parse(events[event]["END"])
      start_date = start_date.replace(tzinfo=tz.gettz("US/Pacific"))
      end_date = end_date.replace(tzinfo=tz.gettz("US/Pacific"))
      starting = start_date - now
      ending = end_date - now
      if ending.days <0:
        del main[event]
      if starting.days < 0: #event started
        countdown = strfdelta(ending,"{days}d{hours}h{minutes}m")
        end_date = end_date.strftime("%d %b %Y %I:%M %p")
        ongoing += f"\n{event}\n+ End : {end_date} ({countdown})"
      else:
        countdown = strfdelta(starting,"{days}d{hours}h{minutes}m")
        start_date = start_date.strftime("%d %b %Y %-I:%M %p")
        upcoming += f"\n{event}\n+ Start : {start_date} ({countdown})"
    ongoing += "```"
    upcoming += "```"
    if ongoing == "```diff\n```":
      ongoing = "```No ongoing event```"
    if upcoming == "```diff\n```":
      upcoming = "```No upcoming event```"
    embed=discord.Embed(color=0xf5dbff)
    embed.add_field(name="Ongoing Events", value=ongoing, inline=False)
    embed.add_field(name="Upcoming", value=upcoming, inline=False)
    with open("event.json","w") as f:
      json.dump(main,f,indent=4)
    return await ctx.send(embed=embed)


  # @commands.command(aliases = ['e'])
  # async def event(self,ctx):
  #   """ View the upcoming and ongoing events """
  #   with open("sdsgc.json", "r") as f:
  #     notes = json.load(f)
    
  #   try:
  #     units = notes[str(tag)]
  #     for i in units:
  #       unit_name = i
  #       unit_ref = notes[str(tag)][unit_name]
  #       break
  #     em = discord.Embed(title=unit_name , description=unit_ref, colour = botcolour)
  #     return await ctx.send(embed = em)
  #   except:
  #     msg = f'There is no note on `{str(unit)}\n`'
  #     suggest = []
  #     for i in nlist:
  #       if tag.capitalize() in list(notes[i].keys())[0]:
  #         suggest.append([list(notes[i].keys())[0],i])
  #     if len(suggest) > 0:
  #       msg += '\n__Suggested:__'
  #       for item in suggest:
  #         msg += f'\n➣{item[0]}\n{ctx.prefix}{item[1]}'
  #     em = discord.Embed(description=msg, colour = discord.Color.red())
  #     return await ctx.send(embed = em)

  # @commands.command(aliases = ['-gc'])
  # async def remove_gc(self,ctx,unit="listing"):
  #   """ Remove the unit's reference """
  #   with open("sdsgc.json", "r") as f:
  #     notes = json.load(f)
  #   if unit == "listing":
  #     notelist = "Remove which one?"
  #     for item in notes:
  #       notelist+="\n➣"
  #       notelist+=str(item)
  #     notelist+=f"\nSend the command again with the unit ie. {ctx.prefix}{notes[0]}"
  #     return await ctx.send(notelist)
  #   tag = unit
  #   try:
  #     del notes[str(tag)]
  #     with open("sdsgc.json","w") as f:
  #         json.dump(notes,f,indent=4)
  #     em = discord.Embed(description=f"Note on {str(tag)} is removed", colour = botcolour)
  #     return await ctx.send(embed = em)
  #   except:
  #     em = discord.Embed(description=f"There is no note on `{str(tag)}`", color = discord.Color.red())
  #     return await ctx.send(embed = em)


def setup(client):
  client.add_cog(Test(client))