import discord
from discord.ext import commands
import os
import pymongo
from pymongo import MongoClient
import random
from PIL import Image


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

# brief='This is the brief description', description='This is the full description'

class SDSGCBanner(commands.Cog):
  """ SDSGC and luck related commands """
  def __init__(self,client):
    self.client = client

  ######## pulling #########
  @commands.command(aliases=['coin'])
  async def coinflip(self,ctx):
    """ Flip a coin for heads or tails """
    out = random.choice(["heads","tails"])
    em = discord.Embed(description = f"Your coinflip results in **{out}**", colour = ctx.author.color)
    await ctx.send(embed = em)

  @commands.command()
  async def checkmyluck(self,ctx):
    """ Check your luck on 3% rates """
    user = ctx.author
    await open_account(user)
    await open_server(user)
    users = mainbank.find_one( {'_id':user.id} )
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    names = user.display_name

    bal = [users["wallet"],users["bank"]]
    if bal[0] < 10:
      em = discord.Embed(description = f"You need 10 {currency} to check luck", colour = discord.Color.red())
      em.set_footer(text= "try !timely")
      return await ctx.send(embed = em)
    luck = []
    result = []
    for i in range(11):
      p = random.randrange(1001)
      p/=10
      luck.append(p)
      if p <= 60:
        result.append("R")
      elif p < 97:
        result.append("SR")
      else:
        result.append("SSR")
    n = len([*filter(lambda x: x > 97, luck)])
    if n < 1:
      pull = f"bad. Don't waste your {currency} dude.."
    else:
      pull = "good. Go pull some SSR!"
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-10}})
    em = discord.Embed(description = f"{names} luck is {pull}\n10{currency} is consumed to check your luck", color=ctx.author.color)
    em.add_field(name = "Results", value = f"{result}")
    em.set_thumbnail(url=ctx.author.avatar_url)
    await ctx.send(embed=em)

  @commands.command()
  @commands.cooldown(1,1,commands.BucketType.user)
  async def pull(self,ctx,arg1=None):
    """ Pull on a random banner unless specified """
    user = ctx.author
    await open_account(user)
    await open_server(user)
    users = mainbank.find_one( {'_id':user.id} )
    guilds = settings.find_one( {'gid':user.guild.id} )
    currency = guilds["emoji"]
    names = user.display_name
    ID = users["_id"]

    bal = [users["wallet"],users["bank"]]
    if bal[0] < 30:
      em = discord.Embed(description = f"You need 30 {currency} to pull", colour = discord.Color.red())
      em.set_footer(text= "try !timely")
      return await ctx.send(embed = em)
      
    if arg1 == None:
      arg = random.choice(["T1","VAL","AM","DZ","MERLIN","FZEL", "REZERO", "ST"])
    else:
      arg = arg1.upper()
    banner = str(arg.upper()) + "Banner"
    dirs = []
    ban6p = ["DZ"]
    ban4p = ["T1","AM","MERLIN","FZEL"]
    ban3p = ["VAL","REZERO","ST"]
    if arg in ban3p:
      for i in range(11):
        p = random.randrange(1001)
        p/=10
        if p <= 60:
          direct(dirs,"R")
        elif p < 97:
          direct(dirs,"SR")
        else:
          direct(dirs,banner)
    elif arg in ban4p:
      for i in range(11):
        p = random.randrange(1001)
        p/=10
        if p <= 60:
          direct(dirs,"R")
        elif p < 96:
          direct(dirs,"SR")
        else:
          direct(dirs,banner)          
    elif arg in ban6p:
      for i in range(11):
        p = random.randrange(1001)
        p/=10
        if p <= 60:
          direct(dirs,"R")
        elif p < 94:
          direct(dirs,"SR")
        else:
          direct(dirs,banner)
    
    im0 = Image.open(dirs[0])
    im1 = Image.open(dirs[1])
    im2 = Image.open(dirs[2])
    im3 = Image.open(dirs[3])
    im4 = Image.open(dirs[4])
    im5 = Image.open(dirs[5])
    im6 = Image.open(dirs[6])
    im7 = Image.open(dirs[7])
    im8 = Image.open(dirs[8])
    im9 = Image.open(dirs[9])
    im10 = Image.open(dirs[10])

    get_concat_h_multi_blank([im0,im1,im2,im3,im4]).save('.//Banner//pull//{}a.jpg'.format(ID))
    get_concat_h_multi_blank([im5,im6,im7,im8,im9,im10]).save('.//Banner//pull//{}b.jpg'.format(ID))
    out1 = Image.open('.//Banner//pull//{}a.jpg'.format(ID))
    out2 = Image.open('.//Banner//pull//{}b.jpg'.format(ID))
    get_concat_v_blank(out1,out2).save('.//Banner//pull//{}c.jpg'.format(ID))

    if arg1 == None:
      quote = "{} randomly pulls on {} Banner\n".format(str(names), arg.upper())
    else:
      quote = "{} pulls on {} Banner\n".format(str(names), arg.upper())
    mainbank.update_one({"_id":user.id}, {"$inc":{"wallet":-30}})
    file = discord.File('.//Banner//pull//{}c.jpg'.format(ID))
    prefix = get_prefix(client,ctx)
    em = discord.Embed(title = quote, description = f"30{currency} is consumed" ,colour = ctx.author.color)
    em.set_thumbnail(url=ctx.author.avatar_url)
    em.set_footer(text=f"use {prefix}help pull")
    # embed.set_author(name = names, icon_url = ctx.author.avatar_url)
    em.set_image(url = "attachment://{}c.jpg".format(ID))
    await ctx.send(embed = em, file = file)


  @commands.command(aliases=['rspvp', 'rs'])
  @commands.cooldown(1,1,commands.BucketType.user)
  async def rselectpvp(self,ctx):
    """ Randomly select 4 units for you """
    names = ctx.author.nick
    if names == None:
      names = ctx.author.name
    dirs = []
    weight = []
    for base, dirs, files in os.walk(".//RSPVP//rspvp"):
        for directories in dirs:
            path = ".//RSPVP//rspvp//" + str(directories)
            f  = os.listdir(path)
            weight.append(len(f))
    while len(dirs)<4:
      path = ".//RSPVP//rspvp"
      files = os.listdir(path)
      cpath = path+"//"+random.choices(files, weights=weight,k=1)[0]
      image = cpath+"//"+random.choice(os.listdir(cpath))
      if len(dirs) == 0:
        dirs.append(image)
      else:
        copy = 0
        for item in dirs:
          if str(cpath) in str(item):
            copy+=1
            break
        if copy>0:
          continue
        else:
          dirs.append(image)

    im0 = Image.open(dirs[0])
    im1 = Image.open(dirs[1])
    im2 = Image.open(dirs[2])
    im3 = Image.open(dirs[3])

    get_concat_h_multi_blank([im0,im1,im2,im3]).save(f'.//RSPVP//pull//{ctx.author.id}.jpg')
    quote = "{} randomly selected units\n".format(str(names))

    file = discord.File(f'.//RSPVP//pull//{ctx.author.id}.jpg')
    embed = discord.Embed(title = quote,colour = ctx.author.color)
    embed.set_image(url = f"attachment://{ctx.author.id}.jpg")
    embed.set_thumbnail(url=ctx.author.avatar_url)
    await ctx.send(embed = embed, file = file)

def direct(directory,rank):
  path = f".//Banner//{rank}"
  files = os.listdir(path)
  image = path+"//"+random.choice(files)
  directory.append(image)

def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

def get_concat_h_blank(im1, im2, color=(0, 0, 0)):
    dst = Image.new('RGB', (im1.width + im2.width, max(im1.height, im2.height)), color)
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def get_concat_v_blank(im1, im2, color=(0, 0, 0)):
    dst = Image.new('RGB', (max(im1.width, im2.width), im1.height + im2.height), color)
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

def get_concat_h_multi_blank(im_list):
    _im = im_list.pop(0)
    for im in im_list:
        _im = get_concat_h_blank(_im, im)
    return _im

def get_concat_h_multi_resize(im_list, resample=Image.BICUBIC):
    min_height = min(im.height for im in im_list)
    im_list_resize = [im.resize((int(im.width * min_height / im.height), min_height),resample=resample)
                      for im in im_list]
    total_width = sum(im.width for im in im_list_resize)
    dst = Image.new('RGB', (total_width, min_height))
    pos_x = 0
    for im in im_list_resize:
        dst.paste(im, (pos_x, 0))
        pos_x += im.width
    return dst

def get_concat_v_multi_resize(im_list, resample=Image.BICUBIC):
    min_width = min(im.width for im in im_list)
    im_list_resize = [im.resize((min_width, int(im.height * min_width / im.width)),resample=resample)
                      for im in im_list]
    total_height = sum(im.height for im in im_list_resize)
    dst = Image.new('RGB', (min_width, total_height))
    pos_y = 0
    for im in im_list_resize:
        dst.paste(im, (0, pos_y))
        pos_y += im.height
    return dst

def get_concat_tile_resize(im_list_2d, resample=Image.BICUBIC):
    im_list_v = [get_concat_h_multi_resize(im_list_h, resample=resample) for im_list_h in im_list_2d]
    return get_concat_v_multi_resize(im_list_v, resample=resample)

def setup(client):
  client.add_cog(SDSGCBanner(client))