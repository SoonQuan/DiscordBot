import discord
from discord.ext import commands,tasks
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

mc_channels = [851668288391872572,851665369726320641]

class Greetings(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.updateMC.start()

    @tasks.loop(minutes=15)
    async def updateMC(self):
      for channel_id in mc_channels:
        try:
          channel = await self.client.fetch_channel(channel_id)
          member_count = channel.guild.member_count
          await channel.edit(name=f'Members: {member_count}')
        except:
          print('smth wrong')

    @updateMC.before_loop
    async def before_updateMC(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def umc(self,ctx):
      for channel_id in mc_channels:
        try:
          channel = await self.client.fetch_channel(channel_id)
          member_count = channel.guild.member_count
          await channel.edit(name=f'Members: {member_count}')
          await ctx.send("Member count updated")
        except:
          pass

    @commands.command()
    async def hello(self,ctx):
      """ Add a GC note for reference """
      await ctx.send('<a:welcome:853659229607690270>')

    @commands.Cog.listener()
    async def on_member_join(self, member):
      if member.guild.id == 825583328111230977:
        channel = member.guild.system_channel
        if channel is not None:
          msg = f"<a:welcome:853659229607690270> Welcome to {member.guild} {member.mention} <a:welcome:853659229607690270>"
          em= discord.Embed(description=f"You are lab rat code **00{member.guild.member_count}**:rat:\n<a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441>",colour = botcolour)
          return await channel.send(content = msg, embed=em)

      elif member.guild.id == 692808940190433360:
        channel = member.guild.system_channel
        if channel is not None:
          msg = f"<a:welcome:853659229607690270> Welcome to Null Community {member.mention} <a:welcome:853659229607690270>"
          em= discord.Embed(description=f"You can post your application here <#694708991321833492>\nRequest for role here <#697647239123959857>\nCombat class role here <#806087564867928094>\n<a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441><a:blobchain:853660327316029441>",colour = botcolour)
          return await channel.send(content = msg, embed=em)


def setup(client):
  client.add_cog(Greetings(client))