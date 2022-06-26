import discord
from discord.ext import commands
import os
from pymongo import MongoClient

from datetime import datetime
from pytz import timezone, all_timezones
import difflib

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]
timezones = db["timezone"]


def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
botcolour = 0x0fa4aab



class Time(commands.Cog):
  """ Time related commands """
  def __init__(self,client):
    self.client = client

  @commands.command(aliases=['set'])
  async def settz(self, ctx, tz):
    """ Set timezone by providing the timezone or location """
    if '/' not in tz:
      zone = await find_timezone(tz)
    else:
      zone = tz
    user = timezones.find_one( {'_id':ctx.author.id} )
    if user is None:
      timezones.insert_one({
        "_id":ctx.author.id,
        "timezone": zone
        })
      embed = discord.Embed(description=f"{ctx.author.display_name}'s timezone has been set to `{zone}`", color=ctx.author.color)
      await ctx.send(embed=embed)
    else:
      timezones.update_one( {"_id": ctx.author.id}, {"$set": {"timezone":zone}} )
      embed = discord.Embed(description=f"{ctx.author.display_name}'s timezone has been set to `{zone}`", color=ctx.author.color)
      await ctx.send(embed=embed)

  @commands.command()
  async def findtz(self, ctx, location):
    """ Find timezone by providing the location """
    geolocator = Nominatim(user_agent="geoapiExercises")
    lad = location
    location = geolocator.geocode(lad)
    obj = TimezoneFinder()
    result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
    embed = discord.Embed(description=f"Time Zone : `{result}`", color=ctx.author.color)
    await ctx.send(embed=embed)
    
  @commands.command()
  async def time(self, ctx, member:discord.Member=None):
    """ Check time of user or member """
    if member == None:
      member = ctx.author
    user = timezones.find_one( {'_id':member.id} )
    if user == None:
      prefix = get_prefix(client,ctx)
      quote = f"Please set your timezone using `{prefix}settz <location>`"
      em = discord.Embed(description = quote, colour = discord.Color.red())
      return await ctx.send(embed=em)
      # user = timezones.find_one( {'_id':self.client.user.id} )
    now_utc = datetime.now(timezone('UTC'))
    now_user = now_utc.astimezone(timezone(user["timezone"]))
    if int(now_user.strftime("%H")) in list(range(7, 20)):
      fmt = f"It's :sunny: %-I:%M %p on %A, %B %d for {member.display_name}. (UTC%z)"
    else:
      fmt = f"It's :crescent_moon: %-I:%M %p on %A, %B %d for {member.display_name}. (UTC%z)"
    em = discord.Embed(description = now_user.strftime(fmt), colour = discord.Color.greyple())
    return await ctx.send(embed=em)

  @commands.command()
  @commands.has_permissions(administrator=True)
  async def setusertz(self, ctx, member:discord.Member=None, tz=None):
    """ (ADMIN) Set timezone by providing the timezone or location """
    if member == None:
      em = discord.Embed(description = f"Who are you setting timezone for?\n{ctx.prefix}setuser <@user> <location>", colour = discord.Color.red())
      return await ctx.send(embed = em)
    elif tz == None:
      em = discord.Embed(description = f"What is {member.display_name} timezone?\n{ctx.prefix}setuser <@user> <location>", colour = discord.Color.red())
      return await ctx.send(embed = em)
    user = timezones.find_one( {'_id':member.id} )
    if '/' not in tz:
      zone = await find_timezone(tz)
    else:
      zone = tz
    if user is None:
      timezones.insert_one({
        "_id":member.id,
        "timezone": zone
        })
      embed = discord.Embed(description=f"{member.display_name}'s timezone has been set to `{zone}`", color=ctx.author.color)
      await ctx.send(embed=embed)
    else:
      timezones.update_one( {"_id": member.id}, {"$set": {"timezone":zone}} )
      embed = discord.Embed(description=f"{member.display_name}'s timezone has been set to `{zone}`", color=ctx.author.color)
      await ctx.send(embed=embed)

  @commands.command()
  @commands.has_permissions(administrator=True)
  async def removeusertz(self, ctx, member:discord.Member=None):
    """ (ADMIN) Remove set timezone of user """
    if member == None:
      em = discord.Embed(description = f"Who are you removing timezone for?\n{ctx.prefix}removeusertz <@user>", colour = discord.Color.red())
      return await ctx.send(embed = em)
    timezones.remove({"_id": member.id})
    embed = discord.Embed(description=f"Timezone removed", color=ctx.author.color)
    await ctx.send(embed=embed)

  @commands.command()
  async def removetz(self, ctx):
    """ Remove set timezone """
    timezones.remove({"_id": ctx.author.id})
    embed = discord.Embed(description=f"Timezone removed", color=ctx.author.color)
    await ctx.send(embed=embed)


  @commands.command()
  async def timein(self, ctx, location=None):
    """ Check time in location """
    if location == None:
      em = discord.Embed(description = f"What location are you looking for?\n{ctx.prefix}timein <location>", colour = discord.Color.red())
      return await ctx.send(embed = em)
    zone = await find_timezone(location)
    now_utc = datetime.now(timezone('UTC'))
    now_location = now_utc.astimezone(timezone(zone))
    if int(now_location.strftime("%H")) in list(range(7, 20)):
      fmt = f"It's :sunny: %-I:%M %p on %A, %B %d in `{zone}`. (UTC%z)"
    else:
      fmt = f"It's :crescent_moon: %-I:%M %p on %A, %B %d in `{zone}`. (UTC%z)"
    em = discord.Embed(description = now_location.strftime(fmt), colour = discord.Color.greyple())
    await ctx.send(embed=em)

  # @commands.command()
  # async def test(self, ctx, *, location=None):
  #   if location != None:
  #     zone = difflib.get_close_matches(location, all_timezones, n=5, cutoff=0.6)
  #     print(zone)
  #     for item in zone:
  #       if location.lower() in item.lower():
  #         dt_mtn = datetime.now(tz=timezone(item))
  #         fmt = f"It's %-I:%M %p on %A, %B %d in `{item}`. (UTC%z)"
  #         print(dt_mtn.strftime(fmt))



async def find_timezone(location):
  geolocator = Nominatim(user_agent="geoapiExercises")
  lad = location
  location = geolocator.geocode(lad)
  obj = TimezoneFinder()
  result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
  return result

def setup(client):
  client.add_cog(Time(client))