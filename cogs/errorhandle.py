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
      logging.warn('Error\n'+str(ctx.message.author.display_name)+'\n'+str(error))
      return await ctx.send(embed=em)

    # elif isinstance(error, commands.CommandNotFound):
    #   em = discord.Embed(title="Don't have this function",
    #                     description=f"Please try something else or use {ctx.prefix}help",
    #                     colour=discord.Color.red())
    #   logging.warn('Error\n'+str(ctx.message.author.display_name)+'\n'+str(error))
    #   return await ctx.send(embed=em)

    elif isinstance(error, commands.BadArgument):
      em = discord.Embed(title="Wrong Argument",
                        description=f"Please try again with the correct arguments\n{ctx.prefix}help [command]",
                        colour=discord.Color.red())
      logging.warn('Error\n'+str(ctx.message.author.display_name)+'\n'+str(error))
      return await ctx.send(embed=em)

    elif isinstance(error, commands.MissingPermissions):
      em = discord.Embed(title="Missing Permission",
                        colour=discord.Color.red())
      em.add_field(name="You don't have the role to do it",
                  value="||You weak||")
      logging.warn('Error\n'+str(ctx.message.author.display_name)+'\n'+str(error))
      return await ctx.send(embed=em)
      
    elif isinstance(error, commands.MissingAnyRole):
      em = discord.Embed(title="Missing Permission",
                        colour=discord.Color.red())
      em.add_field(name="You don't have the role to do it",
                  value="||You weak||")
      logging.warn('Error\n'+str(ctx.message.author.display_name)+'\n'+str(error))
      return await ctx.send(embed=em)

    elif isinstance(error, commands.NotOwner):
      em = discord.Embed(title="Missing Permission",
                        colour=discord.Color.red())
      em.add_field(name="Only bot owner can do this", value="||You weak||")
      logging.warn('Error\n'+str(ctx.message.author.display_name)+'\n'+str(error))
      return await ctx.send(embed=em)

    else:
      logging.warn('Error\n'+str(ctx.message.author.display_name)+'\n'+str(error))
      return print(error)

  @commands.command(hidden=True)
  async def rank(self,ctx,member:discord.Member=None):
    return
  @commands.command(hidden=True)
  async def play(self,ctx):
    return
  @commands.command(hidden=True)
  async def leave(self,ctx):
    return
  @commands.command(hidden=True)
  async def levels(self,ctx):
    return

def setup(client):
  client.add_cog(Error(client))