import discord
import os
from discord.ext import commands, tasks
import pymongo
from pymongo import MongoClient
from itertools import cycle
from keep_alive import keep_alive
from pretty_help import DefaultMenu, PrettyHelp

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]
stonk = db["stonk"]
centralbank = db["centralbank"]


def get_prefix(client, message):
	server = settings.find_one({"gid": message.guild.id})
	return server["prefix"]

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=get_prefix, description="Bot is here for your entertainment",case_insensitive=True, intents=intents)
botcolour = 0x0fa4aab
status = cycle(["with your luck", "with you | try !help"])

menu = DefaultMenu('◀️', '▶️', '❌')
# client.help_command = PrettyHelp(navigation=menu,
#                                  index_title="Help",
#                                  sort_commands=True,
#                                  no_category="Owner",
#                                  color=discord.Colour.blurple())


@client.event
async def on_ready():
	await client.change_presence(activity=discord.Game("with you | try !help"))
	#await change_status.start()
	print('We have logged in as {0.user}'.format(client))

# @tasks.loop(minutes=15)
# async def change_status():
# 	await client.change_presence(activity=discord.Game(next(status)))


@client.event
async def on_guild_join(guild):
	settings.insert_one({
	    "gid": guild.id,
	    "prefix": ">",
	    "emoji": "💎",
	    "droppile": int(500)
	})
	centralbank.insert_one({
	    "gid": guild.id,
	    "taxtime": 0,
	    "centralbank ": 10000
	})
	return


@client.event
async def on_guild_remove(guild):
	settings.remove({"gid": guild.id})
	return

@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
	client.load_extension(f'cogs.{extension}')
	await ctx.send(f"{extension} module has been loaded")


@client.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	await ctx.send(f"{extension} module has been unloaded")


@client.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	client.load_extension(f'cogs.{extension}')
	await ctx.send(f"{extension} module has been reloaded")


for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')


keep_alive()
client.run(os.getenv('TOKEN'))