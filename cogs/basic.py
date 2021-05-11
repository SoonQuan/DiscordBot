import discord
from discord.ext import commands
import os
import pymongo
from pymongo import MongoClient
import random
import asyncio
import json
from google_trans_new import google_translator  

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]


def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
botcolour = 0x0fa4aab
gsmsg_id = 829765626838646814
gschannel_id = 803097378726215723

class BasicFunctions(commands.Cog):
  """ Basic bot commands """
  def __init__(self,client):
    self.client = client

  @commands.Cog.listener()
  async def on_message(self,msg):
    if msg.author.id == self.client.user.id:
      return

    if "escanor animation" in msg.content.lower() or "esca animation" in msg.content.lower():
      await msg.add_reaction("<:laserescanor:747149915385233468>")

    if "noice" in msg.content.lower():
      await msg.add_reaction("<:noice:831113245082779699>")

    if len(msg.content) == 0:
      return
    elif ":" == msg.content[0] and ":" == msg.content[-1]:
      emoji_name = msg.content[1:-1]
      for emoji in msg.guild.emojis:
        if emoji_name == emoji.name:
          await msg.channel.send(str(emoji))
          await msg.delete()
          break
    # await self.client.process_commands(msg)

  @commands.command()
  async def invite(self,ctx):
    """ Invite link to the dev server """
    em = discord.Embed(title="<:questionmark:833703303476150302> Dev Server", url='https://discord.gg/bX5bD9dNvT', description="Click to join dev server", color = botcolour)
    await ctx.send(embed = em)

  @commands.command()
  async def ping(self,ctx):
    """ Check the latency of the bot """
    em = discord.Embed(description = f'Pong! Latency: `{round(self.client.latency*1000)} ms`', color = botcolour)
    await ctx.send(embed = em)

  @commands.command()
  @commands.has_permissions(manage_roles=True)
  async def changeprefix(self,ctx,prefix):
    """ Change the prefix of the bot """
    settings.update_one({"gid":ctx.guild.id}, {"$set":{"prefix":prefix}})
    em = discord.Embed(description=f"Server prefix has been changed to {prefix}", color=botcolour)
    return await ctx.send(embed=em)
    
  @commands.command(aliases = ['+','an'])
  async def add_note(self,ctx,title,*,msg=None):
    """ Check the colour of the bot """
    user = ctx.author
    with open("notes.json", "r") as f:
      notes = json.load(f)
    if msg == None:
      em = discord.Embed(description=f"What is the message", colour = discord.Colour.red())
      return await ctx.send(embed = em)
    if str(user.guild.id) not in notes:
      notes[str(user.guild.id)] = {}
    note = str(msg)
    notes[str(user.guild.id)][str(title)] = note
    with open("notes.json","w") as f:
        json.dump(notes,f,indent=4)
    em = discord.Embed(description=f"Note on {str(title)} saved", colour = botcolour)
    return await ctx.send(embed = em)

  @commands.command(aliases = ['?','rn'])
  async def read_note(self,ctx,title="listing"):
    """ Check the colour of the bot """
    user = ctx.author
    with open("notes.json", "r") as f:
      notes = json.load(f)
    if title == "listing":
      notelist = "List contain:"
      for item in notes[str(user.guild.id)]:
        notelist+="\n➣"
        notelist+=str(item)
      return await ctx.send(notelist)
    try:
      msg = notes[str(user.guild.id)][str(title)]
      em = discord.Embed(description=msg, colour = botcolour)
      return await ctx.send(embed = em)
    except:
      msg = f'{str(title)} not found'
      em = discord.Embed(description=msg, colour = botcolour)
      return await ctx.send(embed = em)


  @commands.command()
  async def repeat(self,ctx, args):
    """ Bot repeats what you said """
    em = discord.Embed(description = args, color = ctx.author.color)
    await ctx.send(embed = em)
    await ctx.message.delete()

  @commands.command(aliases = ['purge'])
  @commands.has_any_role('ADMIN','N⍧ Sovereign', 'G⍧ Archangels', 'K⍧ Kage', 'le vendel' , 'D⍧ Dragon', 'W⍧ Grace', 'R⍧ Leviathan', 'Overseer')
  async def clear(self,ctx, amount=1):
    """ Delete the most recent <amount> of messages """
    def check(m):
        return m.author == ctx.author and m.channel == ctx.message.channel
    await ctx.channel.purge(limit=1)
    await asyncio.sleep(2)
    if amount > 5:
      await ctx.send("Are you sure? yes/y/no/n")
      try:
        msg = await self.client.wait_for("message",timeout= 10, check=check)
        if msg.content.lower() == "yes" or msg.content.lower() == "y":
          await ctx.channel.purge(limit=2)
          await asyncio.sleep(5)
          quotient = amount//5
          remainder = amount%5
          for i in range(quotient):
            await ctx.channel.purge(limit=5)
            await asyncio.sleep(5)
          await ctx.channel.purge(limit=remainder)
        else:
          return
      except asyncio.TimeoutError:
        return await ctx.send("Command Time Out")
    else:
      await ctx.channel.purge(limit=amount+1)
    

  @commands.command(aliases = ['purgemsg', 'clearmsg'])
  @commands.has_any_role('ADMIN','N⍧ Sovereign', 'le vendel' , 'G⍧ Archangels', 'K⍧ Kage', 'D⍧ Dragon', 'W⍧ Grace', 'R⍧ Leviathan', 'Overseer')
  async def deletemsg(self,ctx, msg_id):
    """ Delete the particular message """
    channel = ctx.channel
    message = await channel.fetch_message(int(msg_id))
    await message.delete()
    await ctx.message.delete()

  @commands.command(aliases = ['ae'])
  async def aemoji(self,ctx, msg="listing"):
    """ Send animated emoji """
    with open("aemojis.json", "r") as f:
      aemojis = json.load(f)
    aelist = "List contain:\n"
    if msg == "listing":
      for item in aemojis:
        aelist+="➣"
        aelist+=str(item)
      return await ctx.send(aelist)
    if msg not in aemojis:
      return
    await asyncio.sleep(1)
    await ctx.send(aemojis[str(msg)])
    return await ctx.message.delete()

  @commands.command()
  @commands.has_permissions(manage_roles=True)
  async def embedit(self,ctx,channel_id,msg_id,new_msg):
    """ Edit a particular embed message """
    names = ctx.author.nick
    if names == None:
      names = ctx.author.name  
    channel = self.client.get_channel(int(channel_id))
    message = await channel.fetch_message(int(msg_id))
    em = discord.Embed(description = f"{new_msg}", color=ctx.author.color)
    em.set_footer(text= f"Last updated by {names}")
    await message.edit(embed = em)
    await ctx.message.delete()

  @commands.command(aliases= ['up'])
  @commands.has_any_role('N⍧ Sovereign', 'le vendel' , 'G⍧ Archangels', 'K⍧ Kage', 'D⍧ Dragon', 'W⍧ Grace', 'R⍧ Leviathan')
  async def updatemsg(self,ctx,new_msg):
    """ Update our notice """
    names = ctx.author.nick
    if names == None:
      names = ctx.author.name  
    channel = self.client.get_channel(int(gschannel_id))
    message = await channel.fetch_message(int(gsmsg_id))
    em = discord.Embed(description = f"{new_msg}", color=ctx.author.color)
    em.set_footer(text= f"Last updated by {names}")
    await message.edit(embed = em)
    await ctx.message.delete()

  @commands.command(aliases = ['pl'])
  async def poll(self,ctx,*,msg):
    """ Poll command """
    channel = ctx.channel
    try:
      op1, op2 = msg.split("or")
      txt = f"React with ✅ for {op1} or ❎ for {op2}"
    except:
      await channel.send("Correct Syntax: [Choice 1] or [Choice 2]")
      return
    
    em = discord.Embed(title="Poll", description = txt, color=botcolour)
    message_ = await channel.send(embed=em)
    await message_.add_reaction("✅")
    await message_.add_reaction("❎")
    await ctx.message.delete()

  @commands.command(aliases = ['trans'])
  async def translate(self,ctx, lang="en", *,args="translate <code> <words to translate>"):
    """ Translate your message into the language you want """
    try: 
      t = google_translator()
      a = t.translate(args, lang_tgt=lang)                 
      em = discord.Embed(description = a, color=ctx.author.color)
      await ctx.send(embed = em)
    except:
      em = discord.Embed(title='Look for langauge code here',
                        url='https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes',
                        description= f"For example: !translate <code> <words to translate>",
                        color=discord.Color.red())
      await ctx.send(embed = em)    

def setup(client):
  client.add_cog(BasicFunctions(client))