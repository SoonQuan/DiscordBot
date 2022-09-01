import discord
from discord.ext import commands,tasks
import os, random
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

monlist = [
  '<@385046875340013578>',
  '<@161799396575412225>',
  '<@427113034629120012>',
  '<@329997304780161028>',
  '<@448113801376694275>',
  '<@396121525205336064>',
  '<@350621587684196352>',
  '<@928281897459675227>',
  '<@296586790578683904>',
  '<@374245864387903488>'
  ]

with open("active.json", 'r') as f:
  activedata = json.load(f)
  f.close()

class Greetings(commands.Cog):
    def __init__(self, client):
        self.client = client
        # self.keepactive.start()

    # @tasks.loop(minutes=123)
    # async def keepactive(self):
    #   try:
    #    channel = await self.client.fetch_channel(516246018988441602)
    #    member = random.choice(monlist)
    #    quote = f"{member} {random.choice(activedata['NOTES'])}"
    #    await channel.send(quote)
    #  except:
    #    print("smth wrong")

   # @keepactive.before_loop
   # async def before_keepactive(self):
   #     await self.client.wait_until_ready()

    # @commands.command()
    # async def aaaa(self,ctx):
    #   try:
    #     channel = await self.client.fetch_channel(840799693700071434)
    #     # channel = await self.client.fetch_channel(516246018988441602)
    #     # member = random.choice(monlist)
    #     member = '<@399558274753495040>'
    #     quote = f"{member} {random.choice(activedata['NOTES'])}"
    #     await channel.send(quote)
    #   except:
    #     print("smth wrong")
        
    @commands.command()
    @commands.has_any_role('ADMIN','N⍧ Sovereign', 'le vendel' , 'G⍧ Archangels', 'K⍧ Kage', 'D⍧ Dragon', 'W⍧ Grace', 'R⍧ Leviathan')
    async def umc(self,ctx):
      """ Update member count """
      for channel_id in mc_channels:
        try:
          channel = await self.client.fetch_channel(channel_id)
          member_count = channel.guild.member_count
          await channel.edit(name=f'Members: {member_count}')
        except:
          pass
      return await ctx.send("Member count updated")

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
