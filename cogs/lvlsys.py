import discord
from discord.ext import commands
import os
import pymongo
from pymongo import MongoClient
import asyncio

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]
levelling = db["levelling"]


def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
botcolour = 0x0fa4aab


level = ["Viltriumite officer", "Viltrumite Divine generel", "Viltrum Royal Gaurd"]
levelnum = [5, 10, 15]
bot_channel = 842663522486976542
talk_channels = [825583328111230981,840799693700071434]


class LevelSystem(commands.Cog):
  """ Level System bot commands """
  def __init__(self,client):
    self.client = client

  @commands.Cog.listener()
  async def on_message(self, ctx):
    if ctx.channel.id in talk_channels:
      stats = levelling.find_one({"_id": ctx.author.id})
      if not ctx.author.bot:
        if stats is None:
          newuser = {"_id": ctx.author.id, "xp": 100}
          levelling.insert_one(newuser)
        else:
          xp = stats["xp"]+5
          levelling.update_one({"_id":ctx.author.id}, {"$set":{"xp":xp}})
          lvl = 0
          while True:
            if xp < (50*(lvl**2)+(50*lvl)):
              break
            lvl += 1
          xp -= (50*((lvl-1)**2)+(50*(lvl-1)))
          if xp == 0:
            await ctx.channel.send(f"well done {ctx.author.mention}! you leveled up to **level {lvl}**!")
            for i in range(len(level)):
              if lvl == levelnum[i]:
                await ctx.author.add_roles(discord.utils.get(ctx.author.guild.roles, name=level[i]))
                em = discord.Embed(description=f"{ctx.author.mention} you have gotten role **{level[i]}**!")
                em.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.channel.send(embed=em)

  @commands.command()
  async def rank(self,ctx):
    if ctx.channel.id == bot_channel:
      stats = levelling.find_one({"_id": ctx.author.id})
      if stats is None:
        em = discord.Embed(description=f"You have yet to send any messages, no rank!")
        await ctx.channel.send(embed = em)
      else:
        xp = stats["xp"]
        lvl = 0
        rank = 0
        while True:
          if xp < (50*(lvl**2)+(50*lvl)):
            break
          lvl += 1
        xp -= (50*((lvl-1)**2)+(50*(lvl-1)))
        boxes = int((xp/(200*((1/2)*lvl)))*20)
        rankings = levelling.find().sort("xp",-1)
        for x in rankings:
          rank += 1
          if stats["_id"] == x["_id"]:
            break
        em = discord.Embed(title=f"{ctx.author.display_name}'s level stats")
        em.add_field(name = "Name", value=ctx.author.mention, inline=True)
        em.add_field(name="XP", value=f"{xp}/{int(200*((1/2)*lvl))}", inline=True)
        em.add_field(name="Ranking", value=f"{rank}/{ctx.guild.member_count}", inline=True)
        em.add_field(name=f"Progress Bar [level {lvl}]",value=boxes*":blue_square:"+(20-boxes)*":white_large_square:", inline=False)
        em.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.channel.send(embed = em)

  @commands.command()
  async def leaderboard(self,ctx):
    if ctx.channel.id == bot_channel:
      rankings = levelling.find().sort("xp",-1)
      i = 1
      em = discord.Embed(title="Rankings")
      for x in rankings:
        try:
          temp = await ctx.guild.fetch_member(x["_id"])
          tempxp = x["xp"]
          em.add_field(name=f"{i}: {temp.display_name}", value=f"Total XP: {tempxp}", inline=False)
          i+=1
        except:
          pass
        if i == 5:
          break
      await ctx.channel.send(embed=em)

def setup(client):
  client.add_cog(LevelSystem(client))