import discord
from discord.ext import commands
import os
import asyncio
import pymongo
from pymongo import MongoClient
import time
import datetime
import random

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]
rpg = db["rpg"]

def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
botcolour = 0x0fa4aab
vendorcolour = discord.Color.gold()

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

async def currencygiveaway(reaction_list, amount):
    for id in reaction_list:
      await open_account(id)
      mainbank.update_one({"_id":id.id}, {"$inc":{"wallet":amount}})

class Currency(commands.Cog):
  """ Currency related commands """
  def __init__(self,client):
    self.client = client

  @commands.command()
  @commands.has_permissions(manage_channels=True)
  async def changecurrency(self,ctx, newemoji = ":gem:"):
    """ Change the currency emoji on the server """
    user = ctx.author
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    current = guilds["emoji"]
    settings.update_one( {"gid": user.guild.id}, {"$set": {"emoji":newemoji}} )

    em = discord.Embed(title=f"Currency emoji has been changed from {current} to {newemoji}", color=botcolour)
    await ctx.send(embed=em)
    
  @commands.command()
  @commands.has_any_role('Bot Dev')
  async def setcurrency(self,ctx,member:discord.Member=None,mode="wallet",amount=500):
      """ Set the amount of currency to the target's wallet """
      mainbank.update_one({"_id":member.id}, {"$inc":{f"{mode}":amount}})
      em = discord.Embed(description = f"Currency set for {member.display_name}", color=botcolour)
      await ctx.send(embed = em)

  @commands.command(aliases=['bal', '$'])
  async def balance(self,ctx,member:discord.Member=None):
    """ Check how much you have in your wallet and bank """
    if member == None:
      user = ctx.author
    else:
      user = member
    names = user.display_name
    await open_account(user)
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]

    users = mainbank.find_one( {'_id':user.id} )
    wall = users["wallet"]
    bank = users["bank"]
    wallet_bal = f"{wall:,d}" + " " + currency
    bank_bal = f"{bank:,d}" + " " + currency

    em = discord.Embed(title=f"{names}'s balance", color=user.color)
    em.add_field(name = "Wallet Balance", value= wallet_bal)
    em.add_field(name = "Bank Balance", value= bank_bal)
    em.set_thumbnail(url=user.avatar_url)
    await ctx.send(embed=em)

  @commands.command(aliases=['time','t'])
  async def timely(self,ctx):
    """ Claim your currency """
    names = ctx.author.nick
    if names == None:
      names = ctx.author.name
    user=ctx.author
    await open_account(user)
    await open_server(ctx.author)
    users = mainbank.find_one( {'_id':user.id} )
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    currenttime = time.time()
    # time diff in seconds in float
    timedif = float(currenttime)-users["timelycd"]
    # print(timedif)
    if timedif > 43200: #12 hour
      earnings = 500
      mainbank.update_many({"_id":user.id}, {"$inc":{"wallet":earnings, "timelycd":timedif}})
      em = discord.Embed(description = f"{names} You have gain {earnings} {currency}", colour = ctx.author.color)
      await ctx.send(embed = em)
    else:
      cd = 43200 - timedif
      remaining_time = time.strftime("%HH %MM %SS" ,time.gmtime(cd))
      em = discord.Embed(title="Still on cooldown", description = "Please try again in {}".format(remaining_time), colour = discord.Color.red())
      return await ctx.send(embed = em)


  @commands.command()
  async def withdraw(self,ctx, amount = None):
    """ Withdraw currency out from bank """
    user = ctx.author
    await open_account(user)
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    bal = await update_bank(user)
    if amount == None:
      em = discord.Embed(description = "Please enter the amount", colour = discord.Color.red())
      await ctx.send(embed = em)   
      return
    elif '.' in amount:
      em = discord.Embed(description = "Whole number only!", colour = discord.Color.red())
      await ctx.send(embed = em)    
      return
    
    if amount == "all":
      amount = int(bal[1])
    else:
      amount = int(amount)
      if amount>bal[1]:
        em = discord.Embed(description = f"You don't have that much {currency}!", colour = discord.Color.red())
        await ctx.send(embed = em)
        return
      if amount<=0:
        em = discord.Embed(description = "Amount must be positive", colour = discord.Color.red())
        await ctx.send(embed = em)
        return
    mainbank.update_many({"_id":user.id}, {"$inc":{"wallet":amount, "bank":-1*amount}})
    em = discord.Embed(description = f"You withdraw {amount:,d}{currency}", colour = ctx.author.color)
    return await ctx.send(embed=em)

  @commands.command(aliases =['save','bank'])
  async def deposit(self,ctx, amount = None):
    """ Deposit currency into bank """
    user = ctx.author
    await open_account(user)
    await open_server(ctx.author)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]

    if amount == None:
      em = discord.Embed(description = "Please enter the amount", colour = discord.Color.red())
      await ctx.send(embed = em)   
      return
    elif '.' in amount:
      em = discord.Embed(description = "Whole number only!", colour = discord.Color.red())
      await ctx.send(embed = em)    
      return
    bal = await update_bank(user)
    if amount == "all":
      amount = int(bal[0])
    else:
      amount = int(amount)
      if amount>bal[0]:
        em = discord.Embed(description = f"You don't have that much {currency}!", colour = discord.Color.red())
        await ctx.send(embed = em)
        return
      if amount<=0:
        em = discord.Embed(description = "Amount must be positive", colour = discord.Color.red())
        await ctx.send(embed = em)
        return
    mainbank.update_many({"_id":user.id}, {"$inc":{"wallet":-1*amount, "bank":amount}})
    em = discord.Embed(description = f"You deposit {amount:,d}{currency}", colour = ctx.author.color)
    return await ctx.send(embed=em)

  @commands.command(aliases=['ctransfer', 'give'])
  async def donate(self,ctx,member:discord.Member, amount = None):
    """ Give your target the amount of currency """
    user = ctx.author
    target = member
    await open_account(user)
    await open_account(target)
    await open_server(ctx.author)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    tnames = member.display_name
    if amount == None:
      em = discord.Embed(description = "Please enter the amount", colour = discord.Color.red())
      await ctx.send(embed = em)   
      return
    elif '.' in amount:
      em = discord.Embed(description = "Whole number only!", colour = discord.Color.red())
      await ctx.send(embed = em)    
      return
    bal = await update_bank(user)
    amount = int(amount)

    if amount>bal[0]:
      em = discord.Embed(description = f"You don't have that much {currency}!", colour = discord.Color.red())
      await ctx.send(embed = em)
      return
    if amount<=0:
      em = discord.Embed(description = "Amount must be positive", colour = discord.Color.red())
      await ctx.send(embed = em)
      return
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-1*amount}})
    mainbank.update_one({"_id":target.id}, {"$inc":{"wallet":amount}})

    em = discord.Embed(description = f"You donate {amount:,d}{currency} to {tnames}", colour = ctx.author.color)
    await ctx.send(embed=em)

  @commands.command(aliases=['beg','pickup'])
  async def pickdrops(self,ctx):
    """ Pick up currency from drop pile """
    user = ctx.author
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    await open_account(user)
    users = mainbank.find_one( {'_id':user.id} )
    names = user.display_name
    droppile = guilds["droppile"]
    currenttime = time.time()
    # time diff in seconds in float
    timedif = float(currenttime)-users["begcd"]
    # print(timedif)
    if timedif > 1800: # half hour
      earnings = random.randrange(167)
      if earnings > droppile:
        earnings = droppile
      settings.update_one({"gid":user.guild.id}, {"$inc":{"droppile":-1*earnings}})
      mainbank.update_many({"_id":user.id}, {"$inc":{"wallet":earnings, "begcd":timedif}})
      em = discord.Embed(description = f"{names} You have picked up {earnings} {currency} from the dropped pile", colour = ctx.author.color)
      return await ctx.send(embed = em)
    else:
      cd = 1800 - timedif
      remaining_time = time.strftime("%HH %MM %SS" ,time.gmtime(cd))
      em = discord.Embed(title="Still on cooldown", description = "Please try again in {}".format(remaining_time), colour = discord.Color.red())
      return await ctx.send(embed = em)

  @commands.command(aliases=['throw'])
  async def drop(self,ctx, amount = None):
    """ Drop currency into the drop pile """
    user = ctx.author
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    await open_account(user)
    names = user.display_name
    if amount == None:
      em = discord.Embed(description = "Please enter the amount", colour = discord.Color.red())
      await ctx.send(embed = em)   
      return
    elif '.' in amount:
      em = discord.Embed(description = "Whole number only!", colour = discord.Color.red())
      await ctx.send(embed = em)    
      return
    bal = await update_bank(user)
    if amount == "all":
      amount = int(bal[0])
    else:
      amount = int(amount)
      if amount>bal[0]:
        em = discord.Embed(description = f"You don't have that much {currency}!", colour = discord.Color.red())
        await ctx.send(embed = em)
        return
      elif amount<=0:
        em = discord.Embed(description = "Amount must be positive", colour = discord.Color.red())
        await ctx.send(embed = em)
        return
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-1*amount}})
    settings.update_one({"gid":user.guild.id}, {"$inc":{"droppile":amount}})
    em = discord.Embed(description = f"{names} You dropped {amount:,d} {currency} into the drop pile", colour = ctx.author.color)
    return await ctx.send(embed=em)

  @commands.command()
  async def droppile(self,ctx):
    """ Reveal the drop pile """
    user = ctx.author
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    droppile = guilds["droppile"]
    em = discord.Embed(description = f"There are {droppile:,d} {currency} in the drop pile", colour = ctx.author.color)
    return await ctx.send(embed=em)

  @commands.command(aliases=['clb'])
  async def cleaderboard(self,ctx, x = 3):
    """ Check who is the richest """
    await open_server(ctx.author)
    guilds = settings.find_one( {'gid':ctx.author.guild.id} )
    currency = guilds["emoji"]
    users = mainbank.find({})
    lb = {}
    total = []
    for user in users:
      ID = int(user["_id"])
      total_amt = user["wallet"] + user["bank"]
      lb[total_amt] = ID
      total.append(total_amt)
    total = sorted(total,reverse=True)
    em = discord.Embed(title = f"{currency} Top {x} Richest Peeps {currency}", description = f"This is the total amount of {currency} in bank and wallet", color = botcolour)
    index = 1
    topmember = await self.client.fetch_user(lb[total[0]])
    for amt in total:
      id_ = lb[amt]
      member = await self.client.fetch_user(int(id_))
      name = member.display_name
      em.add_field(name = f"{index}. {name}", value = f"{amt:,d} {currency}", inline = False)
      if index == x:
        break
      else:
        index += 1
    em.set_thumbnail(url=topmember.avatar_url)
    await ctx.send(embed = em)

  @commands.command(aliases=['betroll', 'br'])
  @commands.cooldown(10,300,commands.BucketType.user)
  async def bet(self,ctx, amount = None):
    """ Bet the amount and get 2x,4x or even 10x back """
    user = ctx.author
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    await open_account(user)
    names = user.display_name
    if amount == None:
      em = discord.Embed(description = "Please enter the amount", colour = discord.Color.red())
      await ctx.send(embed = em)   
      return
    elif '.' in amount:
      em = discord.Embed(description = "Whole number only!", colour = discord.Color.red())
      await ctx.send(embed = em)    
      return
    bal = await update_bank(user)
    if amount == "all":
      amount = int(bal[0])
    else:
      amount = int(amount)
      if amount>bal[0]:
        em = discord.Embed(description = f"You don't have that much {currency}!", colour = discord.Color.red())
        await ctx.send(embed = em)
        return
      if amount<=0:
        em = discord.Embed(description = "Amount must be positive", colour = discord.Color.red())
        await ctx.send(embed = em)
        return
    roll = random.randrange(101)
    earning = int(amount)
    if roll < 67:
      earning = 0
      mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-1*amount}})
      em = discord.Embed(description = f"{names} has rolled {roll}. Too bad you lost {amount:,d}{currency}", colour = ctx.author.color)
      return await ctx.send(embed = em)
    elif roll < 91:
      earning*=2
      mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":amount}})
      em = discord.Embed(description = f"{names} has rolled {roll}. You have won {earning:,d}{currency} for rolling above 66!", colour = ctx.author.color)
      await ctx.send(embed = em)
    elif roll < 100:
      earning*=4
      mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":3*amount}})
      em = discord.Embed(description = f"{names} has rolled {roll}. You have won {earning:,d}{currency} for rolling above 90!", colour = ctx.author.color)
      await ctx.send(embed = em)
    else:
      earning*=10
      mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":9*amount}})
      em = discord.Embed(description = f"{names} has rolled {roll}. You have won {earning:,d}{currency} for rolling 100!", colour = ctx.author.color)
      await ctx.send(embed = em)

  @commands.command(aliases=['w'])
  @commands.cooldown(10,300,commands.BucketType.user)
  async def wheel(self,ctx, amount = None):
    """ Spin the wheel to get the multiple of it back """
    user = ctx.author
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    await open_account(user)
    names = user.display_name

    if amount == None:
      em = discord.Embed(description = "Please enter the amount", colour = discord.Color.red())
      await ctx.send(embed = em)   
      return
    elif '.' in amount:
      em = discord.Embed(description = "Whole number only!", colour = discord.Color.red())
      await ctx.send(embed = em)    
      return
    bal = await update_bank(user)
    if amount == "all":
      amount = int(bal[0])
    else:
      amount = int(amount)
      if amount>bal[0]:
        em = discord.Embed(description = f"You don't have that much {currency}!", colour = discord.Color.red())
        await ctx.send(embed = em)
        return
      if amount<=0:
        em = discord.Embed(description = "Amount must be positive", colour = discord.Color.red())
        await ctx.send(embed = em)
        return

    wheel = [1.5, 1.7, 2.4, 0.2, 1.2, 0.1, 0.3, 0.5]
    arrow = ["↖","⬆","↗","⬅","➡","↙","⬇","↘"]
    
    roll = random.randrange(9)
    earning = int(amount)
    earning = int(earning*wheel[roll])
    arr = arrow[roll]

    em = discord.Embed(title=f"{names} used {amount:,d} {currency} to win {earning:,d} {currency}",
    description = f"| `1.5` | `1.7` | `2.4` |\n| `0.2` | {arr} | `1.2` |\n| `0.1` | `0.3` | `0.5` |", 
    colour = ctx.author.color)
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":earning-amount}})
    return await ctx.send(embed = em)

  @commands.command()
  @commands.is_owner()
  async def gstart(self,ctx, mins : int, * , prize: int):
    """ Start a currency giveaway """
    await ctx.message.delete()
    await open_server(ctx.author)
    guilds = settings.find_one( {'gid':ctx.author.guild.id} )
    currency = guilds["emoji"]
    embed = discord.Embed(title = "Currency Giveaway!", description = f"{prize:,d}{currency}", color = ctx.author.color)

    end = datetime.datetime.utcnow() + datetime.timedelta(seconds = mins*60) 

    embed.add_field(name = "Ends At:", value = f"{end} UTC")
    embed.set_footer(text = f"Ends {mins} mintues from now! React to claim")

    my_msg = await ctx.send(embed = embed)

    await my_msg.add_reaction(currency)
    await asyncio.sleep(mins*60)

    new_msg = await ctx.channel.fetch_message(my_msg.id)
    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(self.client.user))

    await currencygiveaway(users, prize)

    em = discord.Embed(title = "Currency Giveaway Ended!", description = f"{prize:,d} {currency} given to those reacted", color = ctx.author.color)
    await ctx.send(embed = em)

  @commands.command(aliases=['ld'])
  @commands.is_owner()
  async def luckydraw(self,ctx,length:int = 10):
    """ Start a luckdraw giveaway """
    def check(m):
      return m.channel == ctx.message.channel and m.author == ctx.author
    embed = discord.Embed(title = "Luckdraw Giveaway!", description = f"Please enter the list of names", color = ctx.author.color)
    MAINMSG = await ctx.send(embed = embed)
    namelist = []
    participant = "Participants:\n"
    while len(namelist) < length:
      try:
          NAMES = await self.client.wait_for("message",timeout= 15, check=check)
          if ", " in NAMES.content:
            for NAME in NAMES.content.split(", "):
              namelist.append(NAME)
              participant += f"\n{NAME}"
            embed2 = discord.Embed(title = "Luckdraw Giveaway!", description = participant, color = ctx.author.color)
            await MAINMSG.edit(embed = embed2)
          elif "," in NAMES.content:
            for NAME in NAMES.content.split(","):
              namelist.append(NAME)
              participant += f"\n{NAME}"
            embed2 = discord.Embed(title = "Luckdraw Giveaway!", description = participant, color = ctx.author.color)
            await MAINMSG.edit(embed = embed2)
          elif len(NAMES.content) <= 30:
            namelist.append(NAMES.content)
            participant += f"\n{NAMES.content}"
            embed2 = discord.Embed(title = "Luckdraw Giveaway!", description = participant, color = ctx.author.color)
            await MAINMSG.edit(embed = embed2)
          else:
              em = discord.Embed(title="Input Error", description = f"Please input name in the following orders\n[person1], [person2], [person3]...\n\n**OR**\n\n[person1]\n[person2]\n...", colour = discord.Color.red())
              await ctx.send(embed = em)
      except asyncio.TimeoutError:
        if len(namelist) == 0:
          em = discord.Embed(title="Empty List", description = f"Please input name in the following orders\n[person1], [person2], [person3]...\n\n**OR**\n\n[person1]\n[person2]\n...", colour = discord.Color.red())
          await ctx.send(embed = em)
        else:
          winner = random.choice(namelist)
          em1 = discord.Embed(description = "**Time is up. Luckydraw starts now**", colour = ctx.author.color)
          em2 = discord.Embed(description = "The luckydraw goes to..", colour = ctx.author.color)
          em3 = discord.Embed(description = "The luckydraw goes to....", colour = ctx.author.color)
          em4 = discord.Embed(title="Congratulations", description = f"The luckydraw goes to **{winner}**", colour = ctx.author.color)
          RESULT = await ctx.send(embed = em1)
          await asyncio.sleep(1)
          await RESULT.edit(embed = em2)
          await asyncio.sleep(1)
          await RESULT.edit(embed = em3)
          await asyncio.sleep(1)
          await RESULT.edit(embed = em4)
    if len(namelist) > length:
      namelist = namelist[0:length]
      participant = "Participants:\n"
      for NAME in namelist:
        participant += f"\n{NAME}"
      embed2 = discord.Embed(title = "Luckydraw Giveaway!", description = participant, color = ctx.author.color)
      await MAINMSG.edit(embed = embed2)
    if len(namelist) == length:
      winner = random.choice(namelist)
      em1 = discord.Embed(description = "**List is full. Luckydraw starts now**", colour = ctx.author.color)
      em2 = discord.Embed(description = "The luckydraw goes to..", colour = ctx.author.color)
      em3 = discord.Embed(description = "The luckydraw goes to....", colour = ctx.author.color)
      em4 = discord.Embed(title="Congratulations", description = f"The luckydraw goes to **{winner}**", colour = ctx.author.color)
      RESULT = await ctx.send(embed = em1)
      await asyncio.sleep(1)
      await RESULT.edit(embed = em2)
      await asyncio.sleep(1)
      await RESULT.edit(embed = em3)
      await asyncio.sleep(1)
      await RESULT.edit(embed = em4)      

  @commands.command()
  @commands.is_owner()
  async def resettimely(self,ctx, member:discord.Member=None):
    """ Restart timely for all unless specified """
    if member == None:
      users = mainbank.find( {} )
      for user in users:
        mainbank.update_one({"_id":user["_id"]}, {"$set":{"timelycd":0.0}})
      em = discord.Embed(description = "Timely reset for everyone", color = botcolour)
      await ctx.send(embed = em)
    else:
      await open_account(member)
      names = member.display_name
      mainbank.update_one({"_id":member.id}, {"$set":{"timelycd":0.0}})
      em = discord.Embed(description = f"Timely reset for {names}", color = botcolour)
      await ctx.send(embed = em)

  @commands.command()
  async def vendor(self,ctx):
    """ Check what does the vendor sell """
    user = ctx.author
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    weaponry  = rpg.find_one( {'id':"weaponry"} )
    display = "Dagger|🗡️: Increase rob success by 1%\nShield|🛡️: Decrease rob success by 1%"
    em = discord.Embed(title = "Weapon Vendor", description = display, color=vendorcolour)
    for item in weaponry:
      if item == "_id" or item == "id":
        continue
      name = item
      pricing = weaponry[item]["price"]
      desc = weaponry[item]["description"]
      em.add_field(name = name, value = f"{desc}| {pricing}{currency}")
    await ctx.send(embed = em)

  @commands.command(aliases=['weaponbag', 'eqbag', 'wpnbag'])
  async def equipmentbag(self,ctx):
    """ Open your equipment bag """
    user = ctx.author
    await open_account(user)
    weaponry = rpg.find_one( {'id':"weaponry"} )
    users = mainbank.find_one( {'_id':user.id} )
    bag = users["weapon"]
    em = discord.Embed(title = "Equipment", color=user.color)
    if len(bag) == 0:
      em.add_field(name = "Empty", value = "You don't have any equip") 
      return await ctx.send(embed = em)
    for item in bag:
      name = item
      emoji = weaponry[name.capitalize()]["description"]
      amount = bag[item]
      em.add_field(name = f"{name} | {emoji}", value = f"Qty: {amount:,d}") 
    return await ctx.send(embed = em)

  @commands.command(aliases=['buywpn'])
  async def buyweapon(self,ctx,item = "None",amount = 1):
    """ Buy weapons from the vendor """
    user = ctx.author
    await open_server(user)
    weaponry = rpg.find_one( {'id':"weaponry"} )
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    await open_account(user)
    res = await wpn_buy(user,item,amount)
    cost = int(res[2])
    if item == "None":
      em = discord.Embed(description = "What would you like?", color=vendorcolour)
      return await ctx.send(embed = em)
    if not res[0]:
      if res[1]==1:
        em = discord.Embed(description = f"{item.capitalize()} not sold here", color=vendorcolour)
        return await ctx.send(embed = em)
      if res[1]==2:
        emoji = weaponry[item.capitalize()]["description"]
        em = discord.Embed(description = f"You don't have {cost:,d} {currency} in your wallet to buy {amount:,} {emoji}", color=vendorcolour)
        return await ctx.send(embed = em)
    emoji = weaponry[item.capitalize()]["description"]
    em = discord.Embed(description = f"You just bought {amount:,} {emoji} for {cost:,d}{currency}", color=user.color)
    return await ctx.send(embed = em)



  @commands.command(aliases=['sellwpn'])
  async def sellweapon(self,ctx,item="None",amount = None):
    """ Sell weapons to the vendor *with tax* """
    user = ctx.author
    await open_server(user)
    await open_account(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    users = mainbank.find_one( {'_id':user.id} )
    weaponry = rpg.find_one( {'id':"weaponry"} )
    emoji = weaponry[item.capitalize()]["description"]
    if amount == None:
      amount = 1
    elif amount == "all":
      try:
        amount = users["weapon"][item]
      except:
        em = discord.Embed(description = f"You don't have {emoji} in your bag.", color=vendorcolour)
        return await ctx.send(embed = em)
    if item == "None":
      em = discord.Embed(description = "What would you like to sell?", color=vendorcolour)
      return await ctx.send(embed = em)
    amount = int(amount)
    res = await wpn_sell(user,item,amount)
    cost = int(res[2])
    if not res[0]:
      if res[1]==1:
        em = discord.Embed(description = f"We don't accept {item.capitalize()} here!", color=vendorcolour)
        return await ctx.send(embed = em)
      if res[1]==2:
        em = discord.Embed(description = f"You don't have {amount:,} {emoji} in your bag.", color=vendorcolour)
        return await ctx.send(embed = em)
      if res[1]==3:
        em = discord.Embed(description = f"You don't have {emoji} in your bag.", color=vendorcolour)
        return await ctx.send(embed = em)
    em = discord.Embed(description = f"You just sold {amount:,} {emoji} for {cost:,d}{currency}", color=user.color)
    return await ctx.send(embed = em)

  @commands.command(aliases=['hl'])
  @commands.cooldown(5,900,commands.BucketType.user)
  async def highlow(self,ctx):
    """ Guess if the hidden number is higher/lower/equal """
    user = ctx.author
    def check(m):
        return m.author == ctx.author and m.channel == ctx.message.channel
    user = ctx.author
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    await open_account(user)
    names = user.display_name
    bal = await update_bank(user)
    if bal[0] < 100:
      em = discord.Embed(description = f"{names} You need 100 {currency} to play highlow", colour = discord.Color.red())
      em.set_footer(text= f"try {ctx.prefix}timely")
      return await ctx.send(embed = em)

    number1 = 0
    number2 = 0
    while number1 == number2:
      number1 = random.randint(1, 100)
      number2 = random.randint(1, 100)
    outcome = "equal"
    if number2 > number1:
      outcome = "higher"
    elif number2 < number1:
      outcome = "lower"
    em = discord.Embed(description = f'{names} I have a number between `1 and 100`\nYou have 10 second to guess if it is **higher** or **lower** or **equal** to `{number1}`.',
    colour = ctx.author.color)
    await ctx.send(embed = em)
    try:
      guess = await self.client.wait_for("message",timeout= 10, check=check)
      if guess.content.lower() == "equal" and guess.author==user:
        mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":9900}})
        em = discord.Embed(description = f'You got it! The number is `{number2}`.\nYou win 10,000 {currency}', colour = ctx.author.color)
        return await ctx.send(embed = em)
      elif guess.content.lower() == outcome and guess.author==user:
        mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":100}})
        em = discord.Embed(description = f'You got it! The number is `{number2}`.\nYou win 100 {currency}', colour = ctx.author.color)
        return await ctx.send(embed = em)
      elif guess.content.lower() != outcome and guess.author==user:
        mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-100}})
        em = discord.Embed(description = f"You lost. The number is `{number2}`.\nYou lose 100 {currency}", colour = ctx.author.color)
        return await ctx.send(embed = em)
    except asyncio.TimeoutError:
      em = discord.Embed(description = f"You took too long. The number is `{number2}`.\n You wasted your chance", colour = discord.Color.red())
      return await ctx.send(embed = em)


async def wpn_buy(user,item_name,amount):
    item_name = item_name.lower()
    weaponry = rpg.find_one( {'id':"weaponry"} )
    name_ = None
    for item in weaponry:
        name = item.lower()
        if name == item_name:
            name_ = name
            pricing = weaponry[item.capitalize()]["price"]
            break
    if name_ == None:
        return [False,1,0]
    cost = pricing*amount
    users = mainbank.find_one( {'_id':user.id} )
    bal = [users["wallet"],users["bank"]]
    if bal[0]<cost:
        return [False,2,cost]
    try:
        t = None
        for thing in users["weapon"]:
            n = thing
            if n == item_name:
                mainbank.update_one( {"_id":user.id}, {"$inc":{f"weapon.{thing}":amount}} )
                t = 1
                break
        if t == None:
            mainbank.update_one( {"_id":user.id}, {"$set":{f"weapon.{item_name}":amount}} )
    except:
        mainbank.update_one( {"_id":user.id}, {"$set":{f"weapon.{item_name}":amount}} )
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-1*cost}})
    return [True,"Worked",cost]

async def wpn_sell(user,item_name,amount,pricing = None):
    item_name = item_name.lower()
    weaponry = rpg.find_one( {'id':"weaponry"} )
    name_ = None
    rate = 1/10 #change for future
    for item in weaponry:
        name = item.lower()
        if name == item_name:
            name_ = name
            if pricing==None:
                pricing = rate*weaponry[item.capitalize()]["price"]
            break
    if name_ == None:
        return [False,1,0]
    cost = int(pricing)*amount
    users = mainbank.find_one( {'_id':user.id} )
    t = None
    for thing in users["weapon"]:
        n = thing
        if n == item_name:
            old_amt = users["weapon"][thing]
            new_amt = int(old_amt) - int(amount)
            if new_amt < 0:
                return [False,2,cost]
            mainbank.update_one( {"_id":user.id}, {"$inc":{f"weapon.{thing}":-1*amount}} )
            t = 1
            break
    if t == None:
        return [False,3,cost]
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":cost}})
    return [True,"Worked",cost]



def setup(client):
  client.add_cog(Currency(client))