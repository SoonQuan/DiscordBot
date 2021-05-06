import discord
import os
from discord.ext import commands, tasks
import pymongo
from pymongo import MongoClient
from itertools import cycle
import logging
from keep_alive import keep_alive
from pretty_help import DefaultMenu, PrettyHelp



logging.basicConfig(filename="log.dat", filemode="a+",format='%(asctime)s: %(message)s', level=logging.CRITICAL)
logging.critical('~~~~~~ Admin logged in ~~~~~~')

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]
stonk = db["stonk"]

def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

client = commands.Bot(command_prefix=get_prefix, description="Bot is here for your entertainment",case_insensitive=True)
botcolour = discord.Color.red()
status = cycle(["with your luck", "with you | try !help"])

menu = DefaultMenu('◀️', '▶️', '❌')
client.help_command = PrettyHelp(
  navigation=menu,
  index_title="Help",
  sort_commands=True,
  no_category="Owner",
  color=discord.Colour.blurple()
  ) 


@client.event
async def on_ready():
  change_status.start()
  print('We have logged in as {0.user}'.format(client))

@tasks.loop(minutes=11)
async def change_status():
  await client.change_presence(activity=discord.Game(next(status)))

@client.event
async def on_guild_join(guild):
  settings.insert_one({
  "gid":guild.id,
  "prefix":">",
  "emoji": "💎",
  "droppile": int(500)
  })
  return

@client.event
async def on_guild_remove(guild):
  settings.remove({"gid":guild.id})
  return

@client.command()
@commands.is_owner()
async def load(ctx, extension):
  client.load_extension(f'cogs.{extension}')

@client.command()
@commands.is_owner()
async def unload(ctx, extension):
  client.unload_extension(f'cogs.{extension}')

@client.command()
@commands.is_owner()
async def reload(ctx, extension):
  client.unload_extension(f'cogs.{extension}')
  client.load_extension(f'cogs.{extension}')
  await ctx.send(f"{extension} module has been reloaded")

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    client.load_extension(f'cogs.{filename[:-3]}')

# @client.command()
# async def pong(ctx):
#   user = mainbank.find_one( {'_id':ctx.author.id} )
#   for item in user:
#     print(item)
#     if item == "stonk":
#       for thing in user[item]:
#         print(thing)
#         if thing == "session1":
#           print("stonk here")
#           mainbank.update_one({"_id":ctx.author.id}, {"$unset":{f"{item}.{thing}":""}})
#           print("stonk out")



keep_alive()
client.run(os.getenv('TOKEN'))