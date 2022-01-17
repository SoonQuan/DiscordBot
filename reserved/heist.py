import discord
from discord.ext import commands
import os
import pymongo
from pymongo import MongoClient
import asyncio
import random
import json
import time

"""
Grand Heist
|
----- Initiator
      |
      ----- Initiation Fee 5K
      |
      ----- Status
            |
            ----- Alive
            |
            ----- Dead
            |
            ----- Jailed
                  |
                  ----- Pay to be bailed out
            |
            ----- Heisting
      |
      ----- Level
            |
            ----- Gain Exp based of how many times they rob and Heist
                  |
                  ----- Rank = 
                  |
                  ----- Rob give 1
                  |
                  ----- Heist give 10
      |
      ----- Weapon Bonus
|
----- Central Bank
      |
      ----- Level
      |
      ----- Money
      |
      ----- Random Events
            |
            ----- Good
                  |
                  ----- Additional Bonus
            |
            ----- Bad
                  |
                  ----- Jailed
                  |
                  ----- Dead
|
----- Crewlist
      |
      ----- Crew
            |
            ----- Participation Fee 2K
            |
            ----- Status
                  |
                  ----- Alive
                  |
                  ----- Dead
                  |
                  ----- Jailed
                        |
                        ----- Pay to be bailed out
                  |
                  ----- Heisting
            |
            ----- Level
            |
            ----- Weapon Bonus
|
----- Weapons
      |
      ----- Bonus
            |
            ----- Reward rates
            |
            ----- Event rates
                  |
                  ----- Good Rate
                  |
                  ----- Bad Rate

"""

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]
centralbank = db["centralbank"]

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

async def open_heist_account(ctx):
  user = centralbank.find_one( {'_id':ctx.id} )
  if user is None:
    centralbank.insert_one({
      "_id": ctx.id, 
      "xp": 100, 
      "level": 1,
      "status": "Alive",
      "timer": 0,
      "weapon": {
        "earnings":{},
        "success": {},
        "survival":{}
      }
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

async def gain_xp(ctx, user, xp=10):
  await open_heist_account(user)
  stats = centralbank.find_one( {'_id':user.id} )
  xp = stats["xp"]+xp
  oldlvl = stats["level"]
  centralbank.update_one({"_id":user.id}, {"$set":{"xp":xp}})
  lvl = 0
  while True:
    if xp < (50*(lvl**2)+(50*lvl)):
      break
    lvl += 1
  centralbank.update_one({"_id":user.id}, {"$set":{"level":lvl}})
  if oldlvl != lvl:
    return await ctx.channel.send(f"Congratulations {user.mention}! Heist leveled up to **level {lvl}**!")

async def update_bank(user):
  await open_account(user)
  users = mainbank.find_one( {'_id':user.id} )
  return [users["wallet"],users["bank"]]

class Heist(commands.Cog):
  """ GrandHeist commands """
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
      await gain_xp(ctx, user, 10)
      await gain_xp(ctx, target, 10)
      return await ctx.send(embed = em)

    grab = int(targets["wallet"]/random.randrange(101))
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":grab}})
    mainbank.update_one({"_id":target.id}, {"$inc":{"wallet":-1*grab}})
    em = discord.Embed(title = "Rob Success",description = f'With a success rate of {40+star}%. {names} competed the operation.\n**You robbed {grab:,d}{currency} from {tnames}**', colour = discord.Color.green())
    em.add_field(name="Resources used", value= f"{names} has used {userused} 🗡 and {tnames} has used {targetused} 🛡")
    await gain_xp(ctx, user, 50)
    await gain_xp(ctx, target, 10)
    return await ctx.send(embed = em)


  @commands.command(aliases=['gheist'])
  @commands.cooldown(1,1,commands.BucketType.guild) # 1 every 15mins/900secs
  async def grandheist(self,ctx):
    """ Group up and heist the target's bank """
    def check(m):
      return m.channel == ctx.message.channel
    user = ctx.author
    names = user.display_name
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    await open_account(user)
    await open_heist_account(user)
    users = mainbank.find_one( {'_id':user.id} )
    cb = centralbank.find_one( {'id':"central"} )
    if cb["heist_start"] == True:
      em1 = discord.Embed(description = 'A Grand Heist is currently ongoing. Please join that instead', colour = discord.Color.red())
      return await ctx.send(embed = em1)

    if users["wallet"] < 5000:
      em = discord.Embed(description = f"You need at least 5000 {currency} in your wallet to initiate a heist.", colour = discord.Color.red())
      return await ctx.send(embed = em)

    em1 = discord.Embed(description = f"{names} is starting a grand heist on the central bank! 5000 {currency} is used.\n Grand Heist will begin in 30 minutes! Join by typing {ctx.prefix}joingrandheist/{ctx.prefix}jgh", colour = user.color)
    # mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-5000}})
    await gain_xp(ctx, user, 100)
    centralbank.update_many({"id":"central"}, {"$set": {"heist_start": True}, "$push": {"heist_crew": user.id}})
    await ctx.send(embed = em1)
    await asyncio.sleep(1200) #20 minutes

    em1 = discord.Embed(description = f"{names} is starting a grand heist on the central bank!\nGather up within the next 10 minutes! Join by typing `{ctx.prefix}joingrandheist`", colour = user.color)
    await ctx.send(embed = em1)
    await asyncio.sleep(600) #10 minutes

    em1 = discord.Embed(description = f"Grand Heist started by {names} is starting now!\n", colour = user.color)
    await ctx.send(embed = em1)


    crewlist = cb["heist_crew"]
    process = await gheist_process(crewlist) # [rob_amount, survivor, jailed, death]
    survivor_num = len(process[1])
    outquote = "**Heist outcome:**"
    if survivor_num == 0:
      outquote += "\n:skull: No one made it out safe :skull:"
    
    outcome = await gheist_outcome(process[0],process[1]) # list
    for i in range(survivor_num):
      useri = await self.client.fetch_user(process[1][i])
      await gain_xp(ctx, useri, 100)
      namei = useri.display_name
      event_chances = random.randint(1,101)
      event_bonus = 0
      if event_chances < 11:
        events = await event("Good")
        outquote += f'\n{events[0].format(namei)}'
        event_bonus = events[1]
      earnings = outcome[i]
      inner = f'\n:gun: `{namei}` has gotten {earnings:,d}(+{event_bonus}) {currency} from the heist'
      outquote += inner
      # mainbank.update_one({"_id":useri.id}, {"$inc":{"wallet":int(earnings+event_bonus)}})

    if survivor_num > 0:
      outquote += "\n\nHowever,"
    for i in range(len(process[2])): # jailed
      useri = await self.client.fetch_user(process[2][i])
      await gain_xp(ctx, useri, 50)
      namei = useri.display_name
      events = await event("Jailed")
      inner = f'\n:chains: {events[0].format(namei)} `{namei}` is busted :chains:'
      outquote += inner
      centralbank.update_many({"_id":useri.id}, {"$set": {"status": "Jailed", "timer": time.time()}})

    for i in range(len(process[3])): # dead
      useri = await self.client.fetch_user(process[3][i])
      await gain_xp(ctx, useri, 50)
      namei = useri.display_name
      events = await event("Dead")
      inner = f'\n:skull: {events[0].format(namei)} `{namei}` is wasted :skull:'
      outquote += inner
      centralbank.update_many({"_id":useri.id}, {"$set": {"status": "Dead", "timer": time.time()}})
    
    rob_amount = int(process[0])
    outquote += f'\n Central Bank has lost a total of {rob_amount:,d} {currency}'
    centralbank.update_many({"id":"central"}, {"$inc":{"funds":0}, "$set": {"heist_start": False, "heist_crew":[]}})
    em1 = discord.Embed(description = outquote, colour = discord.Color.green())
    return await ctx.send(embed = em1)


  @commands.command(aliases=['jgh'])
  async def joingrandheist(self,ctx):
    """ Join the grand heist """
    user = ctx.author
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    await open_account(user)
    await open_heist_account(user)
    users = mainbank.find_one( {'_id':user.id} )
    if users["wallet"] < 2000:
      em = discord.Embed(description = f"You need at least 2000 {currency} in your wallet to join the heist.", colour = discord.Color.red())
      return await ctx.send(embed = em)

    cb = centralbank.find_one( {'id':"central"} )
    if user.id not in cb["heist_crew"]:
      if cb["heist_start"] == True:
        centralbank.update_one({"id":"central"}, {"$push":{"heist_crew": user.id}})
        # mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-2000}})
        em = discord.Embed(description=f':bank::gun: {user.mention} has joined the `Grand Heist` :bank::gun:\n2000 {currency} is used.', color = user.color)
        return await ctx.send(embed = em)
      else:
        em = discord.Embed(description=f':octagonal_sign: Grand Heist is not active yet :octagonal_sign:', color = user.color)
        return await ctx.send(embed = em)
    else:
      em = discord.Embed(description=f':bank::gun: {user.mention} you have already joined the heist :bank::gun:', color = user.color)
      return await ctx.send(embed = em)    

  @commands.command()
  async def status(self,ctx):
    """ Check your current status """
    user = ctx.author
    await open_server(user)
    await open_account(user)
    await open_heist_account(user)
    users = centralbank.find_one( {'_id':user.id} )
    state = users["status"]
    if state == "Alive":
      em = discord.Embed(description=f'{user.mention} You are currently `{state}`', color = user.color)
      return await ctx.send(embed = em)
    currenttime = time.time()
    timedif = float(currenttime)-users["timer"]
    cool = 12600 #3.5 hour
    if state == "Jailed":
      if timedif > cool: 
        centralbank.update_many({'_id':user.id}, {'$set':{"status":"Alive", "timer":0}})
        em = discord.Embed(description=f'{user.mention} You will be released from jailed. Status changed to `Alive`', color = user.color)
        return await ctx.send(embed = em)
      else:
        cd = cool - timedif
        remaining_time = time.strftime("%HH %MM %SS",time.gmtime(cd))
        em = discord.Embed(description=f'{user.mention} You are currently `{state}`. Check again in {remaining_time} to be released', color = user.color)
        return await ctx.send(embed = em)
    elif state == "Dead":
      if timedif > cool:
        centralbank.update_many({'_id':user.id}, {'$set':{"status":"Alive", "timer":0}})
        em = discord.Embed(description=f'{user.mention} You will be revived. Status changed to `Alive`', color = user.color)
        return await ctx.send(embed = em)
      else:
        cd = cool - timedif
        remaining_time = time.strftime("%HH %MM %SS",time.gmtime(cd))
        em = discord.Embed(description=f'{user.mention} You are currently `{state}`. Check again in {remaining_time} to revive', color = user.color)
        return await ctx.send(embed = em)

  @commands.command()
  async def bail(self,ctx, member:discord.Member=None):
    """ Bail somebody out """
    if member == None:
      member = ctx.author
    user = ctx.author
    await open_server(user)
    await open_account(user)
    await open_heist_account(user)
    await open_account(member)
    await open_heist_account(member)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    users = mainbank.find_one( {'_id':user.id} )
    status = centralbank.find_one( {'_id':member.id} )
    if status["status"] == "Alive":
      em = discord.Embed(description=f'What are you doing? {member.display_name} is not in jail', color=botcolour)
      return await ctx.send(embed=em)
    if users["wallet"] < 2000:
      em = discord.Embed(description = f"You need 2000 {currency} for bailing", colour = discord.Color.red())
      return await ctx.send(embed = em)
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-2000}})
    centralbank.update_one({"_id":member.id}, {"$set":{"status":"Alive"}})
    em = discord.Embed(description=f'{user.mention} {member.display_name} has been bailed out with 2000 {currency}', color=user.color)
    return await ctx.send(embed=em)

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
    await gain_xp(ctx, user, 50)
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
                em1 = discord.Embed(description = f"{JOIN.author.display_name} has joined the heist started by {names}!\n**2000 {currency} is used**", colour = JOIN.author.color)
                await ctx.send(embed = em1)
              else:
                em1 = discord.Embed(description = f"{JOIN.author.display_name} has already joined the heist", colour = JOIN.author.color)
                await ctx.send(embed = em1)
      except asyncio.TimeoutError:
        if len(crewlist) == 1:
          em1 = discord.Embed(description = f"{names} Nobody joined you for the heist. Heist is cancelled.", colour = discord.Color.red())
          return await ctx.send(embed = em1)
        else:
          em1 = discord.Embed(description = "**Time is up. Heist start now**", colour = user.color)
          await ctx.send(embed = em1)
          await asyncio.sleep(3) # wait 3 seconds
          break
    if len(crewlist) == maxcrew:
      em1 = discord.Embed(description = "**Crew is full. Heist start now**", colour = user.color)
      await ctx.send(embed = em1)
      await asyncio.sleep(3) # wait 3 seconds

    process = await heist_process(target,crewlist) # [rob_amount, survivor, death]
    survivor_num = len(process[1])
    outquote = "**Heist outcome:**"
    if survivor_num == 0:
      outquote += "\n💀 No one made it out safe."
      em1 = discord.Embed(description = outquote, colour = discord.Color.greyple())
      return await ctx.send(embed = em1)
    
    outcome = await heist_outcome(process[0],survivor_num) # list
    for i in range(len(process[2])):
      useri = await self.client.fetch_user(process[2][i])
      await gain_xp(ctx, useri, 10)
      namei = useri.display_name
      inner = f'\n💀 {namei} did not make it out safe'
      outquote += inner
    outquote += "\n\nHowever,"
    for i in range(survivor_num):
      useri = await self.client.fetch_user(process[1][i])
      await gain_xp(ctx, useri, 50)
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

async def gheist_success_bonus(user):
  stats = centralbank.find_one( {'_id':user} )
  lvl = stats["level"]
  bonus = lvl-1
  if stats["weapon"]["success"] == {}:
    return bonus
  for item in stats["weapon"]["success"]:
    bonus += item["bonus"]
  return bonus

async def gheist_earning_bonus(user):
  stats = centralbank.find_one( {'_id':user} )
  bonus = 1
  if stats["weapon"]["earnings"] == {}:
    return bonus
  for item in stats["weapon"]["earnings"]:
    bonus += item["bonus"]
  return bonus

async def gheist_survival_bonus(user):
  stats = centralbank.find_one( {'_id':user} )
  bonus = 0
  if stats["weapon"]["survival"] == {}:
    return bonus
  for item in stats["weapon"]["survival"]:
    bonus += item["bonus"]
  return bonus

async def gheist_outcome(earning, survivor): # total earning and survivor ids
  earning = int(earning)
  number = int(len(survivor))
  prelist = []
  outcome = []
  for num in range(number-1):
    prelist.append(random.randrange(1,101))
  totalweight = sum(prelist)
  for num in range(number-1):
    outcome.append(int((earning*(number-1)/number)*prelist[num]/totalweight))
  outcome.append(earning-sum(outcome))
  for num in range(number):
    bonus = await gheist_earning_bonus(survivor[num])
    outcome[num] *= bonus
  return outcome  # need to recalculate sum(outcome) to get total lost 

async def gheist_process(crewlist):
  roll = random.randint(1,2750)
  death = []
  jailed = []
  survivor = list(crewlist)
  crew_number = len(crewlist) #max crew of 15
  probability = (crew_number**2)*10
  for num in range(crew_number):
    bonus = await gheist_success_bonus(crewlist[num])
    probability += bonus
  if roll <= probability: # winning the heist probability
    cb = centralbank.find_one( {'id':"central"} ) 
    cb_bank = cb["funds"] # access the target bank
    rob_amount = int(cb_bank*random.randint(30,50)/100)
    for crew in crewlist:
      rates = random.randint(1,100)
      sbonus = await gheist_survival_bonus(crew)
      rates += sbonus
      if rates < 21: # 20% to die ---- add the random events here
        death.append(crew)
        survivor.remove(crew)
      elif rates < 41: # 20% to jailed ---- add the random events here
        jailed.append(crew)
        survivor.remove(crew)
    return [rob_amount, survivor, jailed, death]
  else:
    for crew in crewlist:
      rates = random.randint(1,100)
      if rates < 51:
        death.append(crew)
        survivor.remove(crew)
      else:
        jailed.append(crew)
        survivor.remove(crew)
    return [0, [], jailed, death]

async def event(event):
  with open("heist.json", "r") as f:
    events = json.load(f)
  event1 = event.capitalize()
  choice = random.choice(events[event1])
  return choice # [choice[0].format(ctx.author.name), outcome ]


def setup(client):
  client.add_cog(Heist(client))