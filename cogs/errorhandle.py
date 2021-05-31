import discord
from discord.ext import commands
import os
import pymongo
from pymongo import MongoClient
import asyncio
import time
import logging

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",
                    level=logging.WARNING,
                    handlers=[logging.FileHandler("log.dat"),
                    logging.StreamHandler()
    ])
logging.warning('~~~~~~ Admin logged in ~~~~~~')

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]


def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
botcolour = 0x0fa4aab


class Error(commands.Cog):
  """ Basic bot commands """
  def __init__(self,client):
    self.client = client

  # ###### Error handling #######
  @commands.Cog.listener()
  async def on_command_error(self,ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      remaining_time = time.strftime("%HH %MM %SS" ,time.gmtime(int(error.retry_after)))
      em = discord.Embed(
          title="Still on cooldown",
          description="Please try again in {}".format(remaining_time),
          colour=ctx.author.color)
      logging.error(str(error))
      return await ctx.send(embed=em)

    elif isinstance(error, commands.CommandNotFound):
      em = discord.Embed(title="Don't have this function",
                        description=f"Please try something else or use {ctx.prefix}help",
                        colour=discord.Color.red())
      logging.error(str(error))
      return await ctx.send(embed=em)

    elif isinstance(error, commands.MissingPermissions):
      em = discord.Embed(title="Missing Permission",
                        colour=discord.Color.red())
      em.add_field(name="You don't have the role to do it",
                  value="||You weak||")
      logging.error(str(error))
      return await ctx.send(embed=em)
      
    elif isinstance(error, commands.MissingAnyRole):
      em = discord.Embed(title="Missing Permission",
                        colour=discord.Color.red())
      em.add_field(name="You don't have the role to do it",
                  value="||You weak||")
      logging.error(str(error))
      return await ctx.send(embed=em)

    elif isinstance(error, commands.NotOwner):
      em = discord.Embed(title="Missing Permission",
                        colour=discord.Color.red())
      em.add_field(name="Only bot owner can do this", value="||You weak||")
      logging.error(str(error))
      return await ctx.send(embed=em)

    else:
      logging.error(str(error))
      return print(error)


def setup(client):
  client.add_cog(Error(client))