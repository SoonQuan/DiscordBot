import discord
from discord.ext import commands,tasks
import os
import pymongo
from pymongo import MongoClient
import time
import random
import logging

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

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
shopcolour = discord.Color.green()

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
      "weapon":{}
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

class StonkMarket(commands.Cog):
  """ Stonk Market related commands """
  def __init__(self,client):
    self.client = client
    self.updatesshop.start()

  @tasks.loop(seconds=5)
  async def updatesshop(self):
    await transferstonk()
    await weeklystonk()
    await stonklog()
    timing = stonk.find_one( {'id':"timing"} )
    sessionstart = timing["sessionstart"]
    timedif = time.time()-sessionstart
    cool = 25200 # change to cooldown duration 7hr
    if timedif >= cool:
      stonk.update_one({"id":"timing"}, {"$inc":{"sessionstart":timedif}})
      await stonkprice() #see where to put this
      channel = self.client.get_channel(825583328111230981)
      role = channel.guild.get_role(839439064137596938)
      await channel.send(f"{role.mention} shop updated")

      # buytime = timing["buytime"]
      # if buytime == 1:
      #   reactemoji = "<:sqbaby:834387387320762388>"
      #   channel = client.get_channel(703054964200833125)
      #   role = channel.guild.get_role(832076962713305098)
      #   rolechnl = '<#697647239123959857>'
      #   quote = f"{role.mention} Items are now on sale~ Pick them up before the are gone\nReact to {reactemoji} in {rolechnl} to get notified about refreshes"
      #   await channel.send(quote)
      # elif buytime == 0:
      #   reactemoji = "<:sqbaby:834387387320762388>"
      #   channel = self.client.get_channel(703054964200833125)
      #   role = channel.guild.get_role(832076962713305098)
      #   rolechnl = '<#697647239123959857>'
      #   quote = f"{role.mention} Buying all items for said price in shop\nReact to {reactemoji} in {rolechnl} to get notified about refreshes"
      #   await channel.send(quote)

  @updatesshop.before_loop
  async def before_updatesshop(self):
      print('updatesshop waiting...')
      await self.client.wait_until_ready()

  @commands.command(aliases=['shop', 'price'])
  async def stonkshop(self,ctx):
    """ Check the shop """
    user = ctx.author
    await open_server(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    timing = stonk.find_one( {'id':"timing"} )
    sessionstart = timing["sessionstart"]
    timedif = time.time()-sessionstart
    cool = 25200 # change to cooldown duration 8hr
    cd = cool - timedif
    remaining_time = time.strftime("%Hhr %Mmin %Ss" ,time.gmtime(cd))
    market = stonk.find_one( {'id':"market"} )
    pricings = market["Onigiri"]["prices"]
    day = 14-len(pricings)
    footerquote = "There is a total of 14 sessions\nYou can only buy items on the first session where the shop will sell you\nOn second session, it is a break where shop wont buy or sell\nFrom third session onwards, you can sell when you want to\nIf you do not sell the items by the end of the 14th session, they will turn to trash"
    if timing["buytime"] == 1:
      em = discord.Embed(title = "Stonk Shop - items in stock", description = f"Let me sell you something\nSession {day}: Ending in {remaining_time}" , color=shopcolour)
      for item in market:
        if item == "_id" or item == "id":
          continue
        name = item
        pricing = market[item]["baseprice"]
        desc = market[item]["description"]
        em.add_field(name = name, value = f"{desc}| {pricing}{currency}")
      em.set_footer(text = footerquote)
      await ctx.send(embed = em)

    elif timing["buytime"] == 2:
      em = discord.Embed(title = "Stonk Shop - items out of stock", description = f"Let's take a break\nSession {day}: Not buying or selling for {remaining_time}" , color=shopcolour)
      em.set_footer(text = footerquote)
      await ctx.send(embed = em)
    else:
      em = discord.Embed(title = "Stonk Shop - items out of stock", description = f"I will gladly buy from you\nSession {day}: Refresh in {remaining_time}" , color=shopcolour)
      for item in market:
        if item == "_id" or item == "id":
          continue
        name = item
        pricing = market[item]["price"]
        desc = market[item]["description"]
        em.add_field(name = name, value = f"{desc}| {pricing}{currency}")
      em.set_footer(text = footerquote)
      await ctx.send(embed = em)

  @commands.command(aliases=['bag'])
  async def stonkbag(self,ctx):
    """ Open your market bag """
    user = ctx.author
    await open_account(user)
    market = stonk.find_one( {'id':"market"} )
    users = mainbank.find_one( {'_id':user.id} )
    bag = users["stonk"]
    em = discord.Embed(title = "Stonk Bag", color=user.color)
    for item in bag:
      name = item
      emoji = market[name.capitalize()]["description"]
      amount = bag[item]
      em.add_field(name = f"{name} | {emoji}", value = f"Qty: {amount}") 
    await ctx.send(embed = em)


  @commands.command(aliases=['buy'])
  async def stonkbuy(self,ctx,item = "None",amount = 1):
    """ Buy items from market """
    user = ctx.author
    await open_server(user)
    market = stonk.find_one( {'id':"market"} )
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    timing = stonk.find_one( {'id':"timing"} )
    if timing["buytime"] == 1:
      await open_account(user)
      res = await stonk_buy(user,item,amount)
      cost = int(res[2])
      if item == "None":
        em = discord.Embed(description = "What would you like?", color=shopcolour)
        return await ctx.send(embed = em)
      if not res[0]:
        if res[1]==1:
          em = discord.Embed(description = f"{item.capitalize()} not sold here", color=shopcolour)
          return await ctx.send(embed = em)
        if res[1]==2:
          emoji = market[item.capitalize()]["description"]
          em = discord.Embed(description = f"You don't have {cost} {currency} in your wallet to buy {amount} {emoji}", color=shopcolour)
          return await ctx.send(embed = em)
      emoji = market[item.capitalize()]["description"]
      em = discord.Embed(description = f"You just bought {amount} {emoji} for {cost}{currency}", color=user.color)
      return await ctx.send(embed = em)
    elif timing["buytime"] == 2:
      em = discord.Embed(description = "Let's take a break\nNot buying or selling", color=shopcolour)
      await ctx.send(embed = em) 
    else:
      em = discord.Embed(description = "I don't have anything to sell\nIn fact, I'm buying them", color=shopcolour)
      return await ctx.send(embed = em)



  @commands.command(aliases=['sell'])
  async def stonksell(self,ctx,item="None",amount = None):
    """ Sell items to market """
    user = ctx.author
    await open_server(user)
    await open_account(user)
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    timing = stonk.find_one( {'id':"timing"} )
    users = mainbank.find_one( {'_id':user.id} )
    market = stonk.find_one( {'id':"market"} )
    emoji = market[item.capitalize()]["description"]
    if item.lower() == "trash":
      for item in users["stonk"]:
        if item == "trash":
          amount = users["stonk"]["trash"]
          break
      res = await stonk_sell(user,str(item),amount,1)
      # emoji = market[item.capitalize()]["description"]
      em = discord.Embed(description = f"You just sold {amount} {emoji} for {amount}{currency}",color=user.color)
      return await ctx.send(embed = em)
    if amount == None:
      amount = 1
    elif amount == "all":
      try:
        amount = users["stonk"][item]
      except:
        em = discord.Embed(description = f"You don't have {emoji} in your bag.", color=shopcolour)
        return await ctx.send(embed = em)
    if timing["buytime"] == 0:
      res = await stonk_sell(user,item,amount)
      cost = int(res[2])
      if item == "None":
        em = discord.Embed(description = "What would you like to sell?", color=shopcolour)
        return await ctx.send(embed = em)
      if not res[0]:
        if res[1]==1:
          em = discord.Embed(description = f"We don't accept {item.capitalize()} here!", color=shopcolour)
          return await ctx.send(embed = em)
        if res[1]==2:
          # emoji = market[item.capitalize()]["description"]
          em = discord.Embed(description = f"You don't have {amount} {emoji} in your bag.", color=shopcolour)
          return await ctx.send(embed = em)
        if res[1]==3:
          # emoji = market[item.capitalize()]["description"]
          em = discord.Embed(description = f"You don't have {emoji} in your bag.", color=shopcolour)
          return await ctx.send(embed = em)
      # emoji = market[item.capitalize()]["description"]
      em = discord.Embed(description = f"You just sold {amount} {emoji} for {cost}{currency}", color=user.color)
      return await ctx.send(embed = em)
    elif timing["buytime"] == 2:
      em = discord.Embed(description = "Let's take a break\nNot buying or selling", color=shopcolour)
      return await ctx.send(embed = em)       
    else:
      em = discord.Embed(description = "I'm not buying anything currently\nIn fact, I'm selling them", color=shopcolour)
      return await ctx.send(embed = em)

  @commands.command()
  @commands.is_owner()
  async def jumpsession(self,ctx):
    """ Jump session """
    return await stonkprice()

  @commands.command()
  @commands.is_owner()
  async def jumptime(self,ctx,timing=0):
    """ Skip time """
    stonk.update_one({'id':"timing"}, {"$inc":{"sessionstart":timing*60}})


async def stonklog():
  timing = stonk.find_one( {'id':"timing"} )
  rotationstart = timing["rotationstart"]
  out = time.strftime("%d-%b-%Y (%H:%M:%S)",time.gmtime(rotationstart+28800))
  end = time.strftime("%d-%b-%Y (%H:%M:%S)",time.gmtime(rotationstart+(25200*14)+28800))
  a = "week start in: "+ str(out)
  logging.critical(a)
  b = "time now is: " + str(time.strftime("%d-%b-%Y (%H:%M:%S)",time.gmtime(time.time()+28800)))
  logging.critical(b)
  c = "week end in: "+  str(end)
  logging.critical(c)
  d = "time to end: " + str(time.strftime("%d-1Day %HHour %MMin %SSec",time.gmtime( rotationstart+(25200*14)-time.time() )))
  logging.critical(d)
  timea = time.time() - rotationstart
  daya = timea//(25200) +1
  e = "Current session: " + str(daya)
  logging.critical(e)
  f = "###################"
  logging.critical(f)  
  g = "current time is "+ str(time.time())
  return print(g)

async def stonk_buy(user,item_name,amount):
    item_name = item_name.lower()
    market = stonk.find_one( {'id':"market"} )
    name_ = None
    for item in market:
        name = item.lower()
        if name == item_name:
            name_ = name
            pricing = market[item.capitalize()]["baseprice"]
            break
    if name_ == None:
        return [False,1,0]
    cost = pricing*amount
    users = mainbank.find_one( {'_id':user.id} )
    bal = [users["wallet"],users["bank"]]
    if bal[0]<cost:
        return [False,2,cost]
    t = None
    for thing in users["stonk"]:
        n = thing
        if n == item_name:
            mainbank.update_one( {"_id":user.id}, {"$inc":{f"stonk.{thing}":amount}} )
            t = 1
            break
    if t == None:
        mainbank.update_one( {"_id":user.id}, {"$set":{f"stonk.{item_name}":amount}} )
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-1*cost}})
    return [True,"Worked",cost]

async def stonk_sell(user,item_name,amount,pricing = None):
    item_name = item_name.lower()
    market = stonk.find_one( {'id':"market"} )
    name_ = None
    rate = 1 #change for future
    for item in market:
        name = item.lower()
        if name == item_name:
            name_ = name
            if pricing==None:
                pricing = rate*market[item.capitalize()]["price"]
            break
    if name_ == None:
        return [False,1,0]
    cost = pricing*amount
    users = mainbank.find_one( {'_id':user.id} )
    t = None
    for thing in users["stonk"]:
        n = thing
        if n == item_name:
            old_amt = users["stonk"][thing]
            new_amt = old_amt - amount
            if new_amt < 0:
                return [False,2,cost]
            mainbank.update_one( {"_id":user.id}, {"$inc":{f"stonk.{thing}":-1*amount}} )
            t = 1
            break
    if t == None:
        return [False,3,cost]
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":cost}})
    return [True,"Worked",cost]

#################
### algorithm ###
#################

patternDic = {
  'random': [0.2, 0.3, 0.15, 0.35],
  'largespike': [0.5, 0.05, 0.2, 0.25],
  'decreasing': [0.25, 0.45, 0.05, 0.25],
  'smallspike': [0.45, 0.25, 0.15, 0.15]
}

async def weeklystonk():
  market = stonk.find_one( {'id':"market"} )
  for item in market:
    if item == "Trash" or item == "_id" or item == "id":
      continue
    else:
      if len(market[item]["prices"]) != 0:
        return
      else:
        newpat = await newpattern(market[item]["pattern"])
        stonk.update_one({"id":"market"}, {"$set":{f"{item}.pattern":newpat}})
        newbase = random.randrange(90,121)
        rates = []
        if newpat == "random":
          rates = await random_rate()
        elif newpat == "largespike":
          rates = await largespike_rate()
        elif newpat == "decreasing":
          rates = await decreasing_rate()
        elif newpat == "smallspike":
          rates = await smallspike_rate()
        stonk.update_one({"id":"market"}, {"$set":{f"{item}.baseprice":newbase}})
        n = 1
        # print(newpat, ": this is the number of hdays: ", len(rates))
        for rate in rates:
          stonk.update_one({"id":"market"}, {"$set":{f"{item}.prices.session{str(n)}":int(rate*newbase)}})
          n+=1
        stonk.update_one({"id":"timing"}, {"$set":{"rotationstart":time.time()}})

async def stonkprice():
  market = stonk.find_one( {'id':"market"} )
  for item in market:
    if item == "Trash" or item == "_id" or item == "id":
      continue  
    else:
      pricings = market[item]["prices"]
      if len(pricings) == 14:
        stonk.update_one({"id":"timing"}, {"$set":{"buytime":1}})
        for day in pricings:
          stonk.update_one({"id":"market"}, {"$unset":{f"{item}.prices.{day}":""}})
          break
      elif len(pricings) == 13:
        stonk.update_one({"id":"timing"}, {"$set":{"buytime":2}})
        for day in pricings:
          stonk.update_one({"id":"market"}, {"$unset":{f"{item}.prices.{day}":""}})
          break
      elif len(pricings) < 13:
        stonk.update_one({"id":"timing"}, {"$set":{"buytime":0}})
        for day in pricings:
          stonk.update_one({"id":"market"}, {"$set":{f"{item}.price":market[item]["prices"][day]}})
          stonk.update_one({"id":"market"}, {"$unset":{f"{item}.prices.{day}":""}})
          break


async def transferstonk():
  timing = stonk.find_one( {'id':"timing"} )
  buytime = timing["buytime"]
  if buytime == 1:
    users = mainbank.find( {} )
    for user in users:
      trashamt = 0
      bag = user["stonk"]
      for item in bag:
        trashamt += user["stonk"][item]
      mainbank.update_one( {"_id":user["_id"]}, {"$set":
      {"stonk": {"trash": trashamt}}} )


##############
#### rota ####
##############
async def newpattern(pattern):
  states = ["random","largespike","decreasing","smallspike"]
  new = random.choices(states,weights=patternDic[pattern])
  return new[0]
  
async def random_phases():
  # Totalhd = 12
  increase_phase1 = random.randrange(0,7)
  decrease_phase1 = random.choice([2,3])
  increase_temp2 = 7 - increase_phase1
  increase_phase3 = random.randrange(0,increase_temp2)
  increase_phase2 = increase_temp2 - increase_phase3
  decrease_phase2 = 5 - decrease_phase1
  pattern = [increase_phase1,decrease_phase1,increase_phase2,decrease_phase2,increase_phase3]
  return pattern

async def random_rate():
  rates=[]
  phase = await random_phases()
  rates.append(0)
  rates.append(0)
  while phase[0] > 0:
    rate = random.randrange(90,141)/100
    rates.append(rate)
    phase[0]-=1

  dcphase1 = 0
  decrease_phase1 = random.randrange(60,81)/100 #drop 4-10% each hd
  while phase[1] > 0:
    rate = decrease_phase1 - dcphase1*random.randrange(4,11)/100
    dcphase1+=1
    rates.append(rate)
    phase[1]-=1      

  while phase[2] > 0:
    rate = random.randrange(90,141)/100
    rates.append(rate)
    phase[2]-=1

  dcphase2 = 0
  decrease_phase2 = random.randrange(60,81)/100 #drop 4-10% each hd
  while phase[3] > 0:
    rate = decrease_phase2 - dcphase2*random.randrange(4,11)/100
    dcphase2+=1
    rates.append(rate)
    phase[3]-=1

  while phase[4] > 0:
    rate = random.randrange(90,141)/100
    rates.append(rate)
    phase[4]-=1    

  return rates

async def largespike_phases():
  # Totalhd = 12
  steady_dec_phase = random.randrange(1,8)
  sharp_inc_phase = 3
  sharp_dec_phase = 2
  random_dec_phase = 7-steady_dec_phase
  pattern = [steady_dec_phase,sharp_inc_phase,sharp_dec_phase,random_dec_phase]
  return pattern

async def largespike_rate():
  rates=[]
  rates.append(0)
  rates.append(0)
  phase = await largespike_phases()
  sdphase = 0
  steady_dec_phase = random.randrange(85,91)/100
  while phase[0] > 0:
    rate = steady_dec_phase - sdphase*random.randrange(3,6)/100
    sdphase+=1
    rates.append(rate)
    phase[0]-=1      
  rates.append(random.randrange(90,141)/100) # inc hd1
  rates.append(random.randrange(140,201)/100) # inc hd2
  rates.append(random.randrange(200,601)/100) # inc hd3

  rates.append(random.randrange(140,201)/100) # dec hd1
  rates.append(random.randrange(90,141)/100) # dec hd2

  while phase[3] > 0:
    rate = random.randrange(40,91)/100
    rates.append(rate)
    phase[3]-=1

  return rates

async def decreasing_rate():
  rates = []
  rates.append(0)
  rates.append(0)
  base_rate = random.randrange(85,91)/100
  rates.append(base_rate)
  temp_rate = base_rate
  for i in range(11):
    temp_rate -= random.randrange(3,6)/100
    rates.append(temp_rate)
  return rates

async def smallspike_phases():
  decreasing_phase1 = random.randrange(0,8)
  increasing_phase = 5
  decreasing_phase2 = 7-decreasing_phase1
  pattern = [decreasing_phase1,increasing_phase,decreasing_phase2]
  return pattern
  

async def smallspike_rate():
  phase = await smallspike_phases()
  rates = []
  rates.append(0)
  rates.append(0)
  dphase1 = 0
  dphase2 = 0
  decreasing_phase1 = random.randrange(40,91)/100
  while phase[0] > 0:
    rate = decreasing_phase1 - dphase1*random.randrange(3,6)/100
    dphase1+=1
    rates.append(rate)
    phase[0]-=1  
  
  # 5 half day increase
  rates.append(random.randrange(90,141)/100)        #half day 1
  rates.append(random.randrange(90,141)/100)        #half day 2
  max_rate = random.randrange(141,201)
  rates.append(random.randrange(140,max_rate)/100)  #half day 3
  rates.append(max_rate/100)                        #half day 4
  rates.append(random.randrange(140,max_rate)/100)  #half day 5  

  while phase[2] > 0:
    rate = decreasing_phase1 - dphase2*random.randrange(3,6)/100
    dphase2+=1
    rates.append(rate)
    phase[2]-=1  
  return rates # list of 12 elements + 2 zero



def setup(client):
  client.add_cog(StonkMarket(client))