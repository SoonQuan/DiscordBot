import discord
from discord.ext import commands
import os
import pymongo
from pymongo import MongoClient
import asyncio
import random

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]


def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
botcolour = 0x0fa4aab

async def open_account(ctx):
  user = mainbank.find_one( {'_id':ctx.id} )
  if user is None:
    mainbank.insert_one({
      "_id":ctx.id,
      "wallet": 500,
      "bank": 500,
      "timelycd": 0,
      "begcd": 0,
      "stonk": {
        "trash": 0
      },
      "weapon":{"dagger":0,"shield":0}
      })
    return True
  else:
    return False

async def open_server(ctx):
  server = settings.find_one( {'gid':ctx.guild.id} )
  if server is None:
    settings.insert_one({
      "gid":ctx.guild.id,
      "prefix":">",
      "emoji": "💎",
      "droppile": int(500)
      })
    return True
  else:
    return False

async def update_bank(user):
  await open_account(user)
  users = mainbank.find_one( {'_id':user.id} )
  return [users["wallet"],users["bank"]]

class Heist(commands.Cog):
  """ Heist related commands """
  def __init__(self,client):
    self.client = client

  @commands.command()
  async def rob(self,ctx, member:discord.Member=None):
    """ Rob currency from your target's wallet """
    if member == None:
      em = discord.Embed(description = "Who are you robbing?", colour = discord.Color.red())
      return await ctx.send(embed = em)
    elif member == ctx.author:
      em = discord.Embed(description = "You deadass? <:kektf:791245709487505408>", colour = discord.Color.red())
      return await ctx.send(embed = em)    

    user = ctx.author
    target = member
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    await open_account(user)
    await open_account(target)
    users = mainbank.find_one( {'_id':user.id} )
    targets = mainbank.find_one( {'_id':target.id} )
    names = user.display_name
    tnames = target.display_name
    if users["wallet"] < 500:
      em = discord.Embed(description = f"You need over 500{currency} to rob somebody.", colour = discord.Color.red())
      return await ctx.send(embed = em)
    elif targets["wallet"] < 500:
      em = discord.Embed(description = f"They have less than 500{currency}. Pity that poor soul.", colour = botcolour)
      return await ctx.send(embed = em)
    userwpn = int(users["weapon"]["dagger"])
    targetwpn = int(targets["weapon"]["shield"])
    star = userwpn-targetwpn # star is the additional bonus
    if star >= 0:
      star = min(star,50) # <= 50
      userused = targetwpn+star
      targetused = targetwpn
      mainbank.update_one({"_id":user.id}, {"$inc":{"weapon.dagger":-userused}})
      mainbank.update_one({"_id":target.id}, {"$inc":{"weapon.shield":-targetused}})
    elif star < 0:
      star = max(star,-30) # >= -30
      userused = userwpn
      targetused = userwpn+abs(star)
      mainbank.update_one({"_id":user.id}, {"$inc":{"weapon.dagger":-userused}})
      mainbank.update_one({"_id":target.id}, {"$inc":{"weapon.shield":-targetused}})
    
    win_lose = random.randrange(101)
    if win_lose <= 60 - star: # chance to fail robbing
      drop = random.randrange(501)
      mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-1*drop}})
      settings.update_one({"gid":user.guild.id}, {"$inc":{"droppile":drop}})
      em = discord.Embed(title = "Rob failed", description = f"With a success rate of {40+star}%. {names} failed the operation.\n**You dropped {drop} {currency}**", colour = discord.Color.red())
      em.add_field(name="Resources used", value= f"{names} has used {userused} 🗡 and {tnames} has used {targetused} 🛡")
      return await ctx.send(embed = em)

    grab = int(targets["wallet"]/random.randrange(101))
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":grab}})
    mainbank.update_one({"_id":target.id}, {"$inc":{"wallet":-1*grab}})
    em = discord.Embed(title = "Rob Success",description = f'With a success rate of {40+star}%. {names} competed the operation.\n**You robbed {grab:,d}{currency} from {tnames}**', colour = discord.Color.green())
    em.add_field(name="Resources used", value= f"{names} has used {userused} 🗡 and {tnames} has used {targetused} 🛡")
    return await ctx.send(embed = em)

  @commands.command()
  @commands.cooldown(1,900,commands.BucketType.guild) # 1 every 15mins/900secs
  async def heist(self,ctx,member:discord.Member=None):
    """ Group up and heist the target's bank """
    def check(m):
      return m.channel == ctx.message.channel
    user = ctx.author
    target = member
    if target == None:
      em = discord.Embed(description="Who's the target?", colour = discord.Colour.red())
      await ctx.send(embed=em)
    names = user.display_name
    tnames = target.display_name
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    await open_account(user)
    await open_account(target)
    users = mainbank.find_one( {'_id':user.id} )
    if users["wallet"] < 5000:
      em = discord.Embed(description = f"You need at least 5000 {currency} in your wallet to initiate a heist.", colour = discord.Color.red())
      return await ctx.send(embed = em)
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-5000}})
    em1 = discord.Embed(description = f"{names} is starting a heist on {tnames}'s bank! 5000 {currency} is used.\nJoin by typing JOIN HEIST in the next 10 seconds!", colour = user.color)
    await ctx.send(embed = em1)
    crewlist = []
    crewlist.append(user.id)
    maxcrew = 5
    while len(crewlist) < maxcrew:
      try:
          JOIN = await self.client.wait_for("message",timeout= 10, check=check)
          if JOIN.content.upper() == "JOIN HEIST":
            crew = mainbank.find_one( {'_id':JOIN.author.id} ) 
            if JOIN.author.id == target.id:
              em = discord.Embed(description = f"Dude? Heist yourself?", colour = discord.Color.red())
              await ctx.send(embed = em)
            elif crew["wallet"] < 2000:
              em = discord.Embed(description = f"You need at least 2000 {currency} in your wallet to join the heist.", colour = discord.Color.red())
              await ctx.send(embed = em)
            else:
              if JOIN.author.id not in crewlist:
                crewlist.append(JOIN.author.id)
                mainbank.update_one({"_id":JOIN.author.id}, {"$inc":{"wallet":-2000}})
                em1 = discord.Embed(description = f"{JOIN.author.display_name} has joined the heist started by {names}!", colour = JOIN.author.color)
                await ctx.send(embed = em1)
              else:
                em1 = discord.Embed(description = f"{JOIN.author.display_name} has already joined the heist", colour = JOIN.author.color)
                await ctx.send(embed = em1)
      except asyncio.TimeoutError:
        if len(crewlist) == 1:
          em1 = discord.Embed(description = f"{names} Nobody joined you for the heist. Heist is cancelled.", colour = discord.Color.red())
          return await ctx.send(embed = em1)
        else:
          em1 = discord.Embed(description = "Time is up. Heist start now", colour = user.color)
          await ctx.send(embed = em1)
          await asyncio.sleep(3) # wait 3 seconds
          break
    if len(crewlist) == maxcrew:
      em1 = discord.Embed(description = "Crew is full. Heist start now", colour = user.color)
      await ctx.send(embed = em1)
      await asyncio.sleep(3) # wait 3 seconds

    process = await heist_process(target,crewlist) # [rob_amount, survivor, death]
    survivor_num = len(process[1])
    outquote = "Heist outcome:"
    if survivor_num == 0:
      outquote += "\n💀 No one made it out safe."
      em1 = discord.Embed(description = outquote, colour = discord.Color.greyple())
      return await ctx.send(embed = em1)
    
    outcome = await heist_outcome(process[0],survivor_num) # list
    for i in range(len(process[2])):
      useri = await self.client.fetch_user(process[2][i])
      namei = useri.display_name
      inner = f'\n💀 {namei} did not make it out safe'
      outquote += inner
    outquote += "\n\nHowever,"
    for i in range(survivor_num):
      useri = await self.client.fetch_user(process[1][i])
      namei = useri.display_name
      earnings = outcome[i]
      inner = f'\n🔫 {namei} has gotten {earnings} {currency} from the heist'
      outquote += inner
      mainbank.update_one({"_id":useri.id}, {"$inc":{"wallet":earnings}})
    rob_amount = int(process[0])
    outquote += f'\n {tnames} has lost a total of {rob_amount:,d} {currency}'
    mainbank.update_one({"_id":target.id}, {"$inc":{"bank":-rob_amount}})
    em1 = discord.Embed(description = outquote, colour = discord.Color.green())
    return await ctx.send(embed = em1)

async def heist_outcome(earning = 1000, number=10):
  earning = int(earning)
  number = int(number)
  prelist = []
  outcome = []
  for num in range(number-1):
    prelist.append(random.randrange(1,101))
  totalweight = sum(prelist)
  for num in range(number-1):
    outcome.append(int((earning*(number-1)/number)*prelist[num]/totalweight))
  outcome.append(earning-sum(outcome))
  return outcome

async def heist_process(target, crewlist):
  roll = random.randint(1,30)
  death = []
  survivor = crewlist
  crew_number = len(crewlist)
  probability = crew_number**2
  if roll <= probability: # winning the heist
    targets = mainbank.find_one( {'_id':target.id} ) 
    target_bank = targets["bank"] # access the target bank
    rob_amount = int(target_bank*random.randint(30,70)/100)
    for crew in crewlist:
      death_rate = random.randint(1,100)
      if death_rate < 41: # 40% to die
        death.append(crew)
        survivor.remove(crew)
    return [rob_amount, survivor, death]
  else:
    return [0, [], survivor]




def setup(client):
  client.add_cog(Heist(client))