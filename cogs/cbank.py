import discord
from discord.ext import commands, tasks
import os
import pymongo
from pymongo import MongoClient
import time
import yfinance as yf
import random

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
cbcolour = 0x82ba65

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

# async def open_cbank(ctx):
#   server = centralbank.find_one( {'gid':ctx.guild.id} )
#   if server is None:
#     centralbank.insert_one({
#       "gid":ctx.guild.id,
#       "centralbank ": 10000
#       })
#     return True
#   else:
#     return False

class CentralBank(commands.Cog):
  """ Central Bank commands """
  def __init__(self,client):
    self.client = client
    self.taxing.start()

  @tasks.loop(minutes=10)
  async def taxing(self):
    await centraltax(self)

  @taxing.before_loop
  async def before_taxing(self):
      print('taxing waiting...')
      await self.client.wait_until_ready()

  @commands.command()
  async def central(self,ctx):
    user = ctx.author
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    cb = centralbank.find_one( {'id':"central"} )
    taxtime = cb["taxtime"]
    timedif = time.time()-taxtime
    cool = 86400 # change to cooldown duration 1 day
    cd = cool - timedif
    remaining_time = time.strftime("%Hhr %Mmin %Ss" ,time.gmtime(cd))
    funding = cb["funds"]
    rate = cb["rate"]*100
    change = cb["change"]
    funds = f"{funding:,.2f}" + " " + currency 
    em = discord.Embed(title = "Central Bank", description = f"Next taxing in {remaining_time}", color=cbcolour)
    em.add_field(name="Balance", value= f'{funds}\n{change:,.3f}({rate:,.3f}%)')
    em.set_footer(text = footer)
    em.set_thumbnail(url=self.client.user.avatar_url)
    await ctx.send(embed=em)

async def fundstonk():
  data = yf.download(tickers='GOLD', period='10m', interval='5m')
  rate = (data['Adj Close'][1]-data['Adj Close'][0])/data['Adj Close'][0]
  centralbank.update_one({'id':"central"}, {"$set":{"rate":rate}})
  cb = centralbank.find_one( {'id':"central"} )
  change = cb["funds"]*(rate)
  centralbank.update_one({'id':"central"}, {"$set":{"change":change}})
  centralbank.update_one({'id':"central"}, {"$inc":{"funds":change}})
  print(change)
  return

def taxrate(credit):
  if credit <= 5000:
    return 0
  elif credit <= 50000:
    return 1
  elif credit <= 500000:
    return 10
  elif credit < 1000000:
    return 25
  return 50

quote = "Daily tax has been deducted."


footer = "Tax will now be deducted from your bank based of your total credit value DAILY.\nYou credit value is the total currency you have (value you see in !clb)\nThe rates are shown below:\nTier | Credit | Tax rate\n0 | 0 - 5,000 | 0%\n1 | 5,001 - 50,000 | 0.1%\n2 | 50,001 - 500,000 | 1%\n3 | 500,001 - 1,000,000 | 2.5%\n4 | >1,000,000 | 5%\ni.e. you have 500 in wallet and 70k in bank, you credit will be 75k. you will fall into tier 1 and subjected to 0.1% tax on the currency you have in your bank. The central bank will take the tax of 70 currency from your bank."

sqdev_gen = 825583328111230981
null_botspam = 703054964200833125

async def centraltax(self):
  cb = centralbank.find_one( {'id':"central"} )
  taxtime = cb["taxtime"]
  timedif = time.time()-taxtime
  cool = 86400 # change to cooldown duration 1 day
  if timedif >= cool:
    users = mainbank.find( {} )
    for user in users:
      wallet = user["wallet"]
      bank = user["bank"]
      credit = wallet + bank
      taxrates = taxrate(credit)
      taxamount = int(bank*taxrates/1000)
      remain = max(0, bank-taxamount)
      mainbank.update_one( {"_id":user["_id"]}, {"$set":
      {"bank": remain }})
      centralbank.update_one({'id':"central"}, {"$inc":{"funds":taxamount}})
    centralbank.update_one({'id':"central"}, {"$inc":{"taxtime":timedif}})
    channel = self.client.get_channel(sqdev_gen)
    em = discord.Embed(title = "Central Bank", description = quote, color=cbcolour)
    em.set_footer(text = footer)
    em.set_thumbnail(url=self.client.user.avatar_url)
    await channel.send(embed=em)
    await fundstonk()  
  return


async def heist_outcome(ctx, earning = 1000, number=10):
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
  return outcome # a list


def setup(client):
  client.add_cog(CentralBank(client))