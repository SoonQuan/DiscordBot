import discord
from discord.ext import commands
import os
from pymongo import MongoClient
from PIL import Image

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]
timezones = db["timezone"]
sdsgc = db["sdsgcProfile"]


def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
botcolour = 0x0fa4aab

async def open_sdsgc(ctx):
  user = sdsgc.find_one( {'_id':ctx.id} )
  if user is None:
    sdsgc.insert_one({
      "_id":ctx.id,
      "rs_setting": None
      })
    return True
  else:
    return False

class Test(commands.Cog):
  """ Basic bot commands """
  def __init__(self,client):
    self.client = client

  @commands.command(aliases=["np"])
  @commands.is_owner()
  async def newBase(self, ctx):
    # await open_sdsgc(ctx.author)
    # user = sdsgc.find_one( {'_id':ctx.author.id} )
    try:
      sdsgc.remove({"_id":"BASE"})
      print("deleted")
    except:
      print("nothing to deleted")
      pass
    sdsgc.insert_one({
      "_id":"BASE",
      "rs_setting": ""
      })
    allunitsdirs=[]
    allunits=[]
    await ctx.send("Initiating new base")
    for base, dirs, files in os.walk(".//RSPVP//rspvp"):
      for file in files:
        allunitsdirs.append(str(os.path.join(base,file)))
        allunits.append(str(file))
    for num in range(len(allunits)):
      unit = {str(allunits[num]).split('.')[0]: {
        "directory": str(allunitsdirs[num]),
        "owned": True
      } }
      sdsgc.update_one( {"_id": "BASE"}, {"$set": unit })
    return await ctx.send("New Profile Initiated")

  @commands.command()
  async def deleteProfile(self, ctx):
    sdsgc.remove({"_id":ctx.author.id})
    return await ctx.send("Profile deleted")

  @commands.command()
  async def createProfile(self, ctx):
    base = sdsgc.find_one( {'_id': "BASE"} )
    base["_id"] = ctx.author.id
    sdsgc.insert(base)
    return await ctx.send("New Profile Initiated")

  @commands.command()
  async def rssetting(self, ctx, *, msg):
    user = sdsgc.find_one( {'_id': ctx.author.id} )
    if user == None:
      pending_command = self.client.get_command('createProfile')
      await ctx.invoke(pending_command)
      user = sdsgc.find_one( {'_id': ctx.author.id} )    
    sdsgc.update_one({"_id":ctx.author.id}, {"$set":{"rs_setting":msg}})
    return await ctx.send(f"Random select setting set to {msg}")

  @commands.command(aliases=["srs"])
  async def setrs(self, ctx):
    user = sdsgc.find_one( {'_id': ctx.author.id} )
    if user == None:
      pending_command = self.client.get_command('createProfile')
      await ctx.invoke(pending_command)
      user = sdsgc.find_one( {'_id': ctx.author.id} )
    exclude = user["rs_setting"]
    if exclude == None:
      exclude = ""
    pending_command = self.client.get_command('randomselect')
    await ctx.invoke(pending_command,exclude=exclude)

  @commands.command(aliases=["ru"])
  async def removeUnit(self, ctx, *, unitlist):
    user = sdsgc.find_one( {'_id': ctx.author.id} )
    if user == None:
      pending_command = self.client.get_command('createProfile')
      await ctx.invoke(pending_command)
      user = sdsgc.find_one( {'_id': ctx.author.id} )
    unitlist = unitlist.lower().split(',')
    for include in unitlist:
      includelist = include.lower().split(' ')
      filterUnit = []
      for base, direct, files in os.walk(".//RSPVP//rspvp"):
          for file in files:
            filterUnit.append(str(os.path.join(base,file)))
      for i in includelist:
        filterUnit = list(filter(lambda k: i in k.lower(), filterUnit))
      if len(filterUnit) > 1:
        embed = discord.Embed(title=f"More than one {include.upper()} found", description="Please be more specific", colour = discord.Color.red())
        embed.set_footer(text= f"try {ctx.prefix}c {include}")
        return await ctx.send(embed = embed)
      else:
        unit = str(filterUnit[0]).split('/')[-1][0:-4]
        sdsgc.update_one({"_id":ctx.author.id}, {"$set":{f"{unit}.owned":False}})
        await ctx.send(f"{unit} has been removed from {ctx.author.display_name}'s pool")

  @commands.command(aliases=["au"])
  async def addUnit(self, ctx, *, unitlist):
    user = sdsgc.find_one( {'_id': ctx.author.id} )
    if user == None:
      pending_command = self.client.get_command('createProfile')
      await ctx.invoke(pending_command)
      user = sdsgc.find_one( {'_id': ctx.author.id} )
    unitlist = unitlist.lower().split(',')
    for include in unitlist:
      includelist = include.lower().split(' ')
      filterUnit = []
      for base, direct, files in os.walk(".//RSPVP//rspvp"):
          for file in files:
            filterUnit.append(str(os.path.join(base,file)))
      for i in includelist:
        filterUnit = list(filter(lambda k: i in k.lower(), filterUnit))
      if len(filterUnit) > 1:
        embed = discord.Embed(title=f"More than one {include.upper()} found", description="Please be more specific", colour = discord.Color.red())
        embed.set_footer(text= f"try {ctx.prefix}c {include}")
        return await ctx.send(embed = embed)
      else:
        unit = str(filterUnit[0]).split('/')[-1][0:-4]
        sdsgc.update_one({"_id":ctx.author.id}, {"$set":{f"{unit}.owned":True}})
        await ctx.send(f"{unit} has been added to {ctx.author.display_name}'s pool")


def setup(client):
  client.add_cog(Test(client))

"""

        pending_command = self.client.get_command('rselectpvp')
        await ctx.invoke(pending_command)

    print('datetime.now(pytz.timezone("US/Pacific")): ', datetime.now(pytz.timezone("US/Pacific")))


    with open("notes.json","w") as f:
        json.dump(notes,f,indent=4)
        
The dmg formula is:

[(Atk x Card %) x (Crit Damage - CritDef) - Def] x Element + [(Atk x Pierce#) - (Def x Resistance)]

Crit Damage# - if it crits

Pierce # - if you have multiplier like x3 you apply it here as well

Element: Multiply with 1, 0.8 or 1.3 based on type advantage, disadvantage or neutral

Damage from Freeze cards get applied after this initial calculation, so take the value which results from the formula and apply 80% or 200% to it then add it to the initial value
        


  @commands.command()
  async def test(self, ctx):
    #Create an object of GridFs for the above database.
    fs = gridfs.GridFS(image)

    #define an image object with the location.
    file = ".//RSPVP//KAI.jpg"

    #Open the image in read-only format.
    with open(file, 'rb') as f:
        contents = f.read()

    #Now store/put the image via GridFs object.
    fs.put(contents, filename="file")
    
  @commands.command()
  async def test1(self, ctx):
    fs = gridfs.GridFS(image) 
    file = fs.find_one({'filename': 'file'})
    image_ = file.read()
    dirs = ".//RSPVP//" + "downloaded.jpg"
    output = open(dirs,"wb")
    output.write(image_)
    output.close()
    print("DONE")
"""