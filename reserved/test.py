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

  @commands.command()
  async def ttt(self,ctx, member:discord.Member=None):
    """ Resurrect somebody earlier """
    if member == ctx.author:
      print('hi')

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