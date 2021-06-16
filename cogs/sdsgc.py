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
    await ctx.send(datetime.now(tz=tz.gettz("US/Pacific")))

  @commands.command(aliases = ['events'])
  async def event(self,ctx):
    def strfdelta(tdelta, fmt):
      d = {"days": tdelta.days}
      d["hours"], rem = divmod(tdelta.seconds, 3600)
      d["minutes"], d["seconds"] = divmod(rem, 60)
      return fmt.format(**d)

    with open("event.json", "r") as f:
      main = json.load(f)
    events = dict(main)
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
    embed.add_field(name="Upcoming Events", value=upcoming, inline=False)
    with open("event.json","w") as f:
      json.dump(main,f,indent=4)
    return await ctx.send(embed=embed)

def setup(client):
  client.add_cog(SDSGC(client))