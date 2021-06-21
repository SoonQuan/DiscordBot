import discord
from discord.ext import commands,tasks
import os
import pymongo
from pymongo import MongoClient
import asyncio
import json

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
    #     self.updateMC.start()

    # @tasks.loop(minutes=15)
    # async def updateMC(self):
    #   for channel_id in mc_channels:
    #     try:
    #       channel = await self.client.fetch_channel(channel_id)
    #       member_count = channel.guild.member_count
    #       await channel.edit(name=f'Members: {member_count}')
    #     except:
    #       print('smth wrong')

    # @updateMC.before_loop
    # async def before_updateMC(self):
    #     await self.bot.wait_until_ready()

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

    @commands.command()
    @commands.has_any_role('ADMIN','N⍧ Sovereign', 'le vendel' , 'G⍧ Archangels', 'K⍧ Kage', 'D⍧ Dragon', 'W⍧ Grace', 'R⍧ Leviathan')
    async def edit_welcome(self,ctx):
      """ Edit welcome message """
      def check(m):
        return m.author == ctx.author and m.channel == ctx.message.channel
      user = ctx.author
      with open("greet.json", "r") as f:
        notes = json.load(f)
      if str(user.guild.id) not in notes:
        notes[str(user.guild.id)] = {}
        # add new welcome
        em = discord.Embed(description = f'What is the welcome message?', colour = ctx.author.color)
        await ctx.send(embed = em)
        try:
          msg1 = await self.client.wait_for("message",timeout= 60, check=check)
          welcome_msg = msg1.content
          notes[str(user.guild.id)]['WELCOME'] = welcome_msg
          with open("greet.json","w") as f:
            json.dump(notes,f,indent=4)
          em = discord.Embed(description="Welcome message has been set", colour = botcolour)
          return await ctx.send(embed = em)    
        except asyncio.TimeoutError:
          em = discord.Embed(description = f"You took too long... try again later when you are ready", colour = discord.Color.red())
          return await ctx.send(embed = em)
      # send current and then wait for update
      em = discord.Embed(description = notes[str(user.guild.id)]['WELCOME'], colour = botcolour)
      await ctx.send(content ="Current welcome message is below, send the updated one within 60s to update it", embed = em)
      try:
        msg1 = await self.client.wait_for("message",timeout= 60, check=check)
        if msg1.content == 'cancel':
          return await ctx.send("Okay")
        welcome_msg = msg1.content
        notes[str(user.guild.id)]['WELCOME'] = welcome_msg
        with open("greet.json","w") as f:
          json.dump(notes,f,indent=4)
        em = discord.Embed(description="New welcome message has been set", colour = botcolour)
        return await ctx.send(embed = em)    
      except asyncio.TimeoutError:
        em = discord.Embed(description = f"You took too long... try again later when you are ready", colour = discord.Color.red())
        return await ctx.send(embed = em)


    @commands.Cog.listener()
    async def on_member_join(self, member):
      with open("greet.json", "r") as f:
        notes = json.load(f)
      if member.guild.id == 825583328111230977:
        channel = member.guild.system_channel
        if channel is not None:
          msg = f"<a:welcome:853659229607690270> Welcome to {member.guild} {member.mention} <a:welcome:853659229607690270>"
          em= discord.Embed(description=notes[str(member.guild.id)]['WELCOME'],colour = botcolour)
          return await channel.send(content = msg, embed=em)

      elif member.guild.id == 692808940190433360:
        channel = member.guild.system_channel
        if channel is not None:
          msg = f"<a:welcome:853659229607690270> Welcome to Null Community {member.mention} <a:welcome:853659229607690270>"
          em= discord.Embed(description=notes[str(member.guild.id)]['WELCOME'],colour = botcolour)
          return await channel.send(content = msg, embed=em)


def setup(client):
  client.add_cog(Greetings(client))