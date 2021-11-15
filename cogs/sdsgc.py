import discord
from discord.ext import commands
import os, shutil
import pymongo
from pymongo import MongoClient
import random
from PIL import Image
import DiscordUtils
import json
import asyncio
from datetime import datetime
from dateutil import parser, tz


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

class SDSGC(commands.Cog):
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
    banner_list = sorted(["T1","VAL","AM","DZ","MERLIN","FZEL", "REZERO", "ST", "EXARTH", "FBAN", "FGOW","HAWK","SEASON", "RAG1", "RAG2", "RAG3", "SROXY","SMLH", "LUDO", "CUSACK", "EMO", "HMATRONABanner", "HDIANE", "KOF"])
    d={}
    out = []
    if arg1 == "list":
      n = 10
      final = [banner_list[i * n:(i + 1) * n] for i in range((len(banner_list) + n - 1) // n )]
      for i in range(len(final)):
        d["Page{0}".format(i+1)] = "\n".join(final[i])
      for page in list(d.keys()):
        out.append(discord.Embed(title="Banner list:",description=d[page], color=ctx.author.color))
      if len(final) == 1:
        em = discord.Embed(title="Banner list:",description=d['Page1'], color=ctx.author.color)
        return await ctx.send(embed=em)
      paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
      paginator.add_reaction('⏮️', "first")
      paginator.add_reaction('⏪', "back")
      paginator.add_reaction('🔐', "lock")
      paginator.add_reaction('⏩', "next")
      paginator.add_reaction('⏭️', "last")
      embeds = out
      return await paginator.run(embeds)
    if arg1 == None:
      arg = random.choice(banner_list)
    elif arg1.upper() not in banner_list:
      em = discord.Embed(description = 'There is no such banner', color = discord.Color.red())
      return await ctx.send(embed = em)
    else:
      arg = arg1.upper()

    banner = str(arg.upper()) + "Banner"
    dirs = []
    ban6p = ["DZ"]
    ban4p = ["T1","AM","MERLIN","FZEL","FBAN","LUDO", "CUSACK", "FGOW"]
    ban3p = ["VAL","REZERO","ST","EXARTH","HAWK","SEASON", "RAG1", "RAG2", "RAG3", "SROXY", "SMLH", "EMO", "HMATRONABanner", "HDIANE", "KOF"]

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
    get_concat_v_blank(out1,out2,(47,49,54)).save('.//Banner//pull//{}c.jpg'.format(ID))

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
    os.remove('.//Banner//pull//{}a.jpg'.format(ID))
    os.remove('.//Banner//pull//{}b.jpg'.format(ID))
    return os.remove('.//Banner//pull//{}c.jpg'.format(ID))

  @commands.command()
  @commands.cooldown(1,1,commands.BucketType.user)
  async def banner(self,ctx,arg1="list"):
    """ Check the banner listed """
    user = ctx.author
    await open_account(user)
    await open_server(user)
    users = mainbank.find_one( {'_id':user.id} )
    ID = users["_id"]

    banner_list = sorted(["T1","VAL","AM","DZ","MERLIN","FZEL", "REZERO", "ST", "EXARTH","FBAN", "FGOW","HAWK","SEASON", "RAG1", "RAG2", "RAG3", "SROXY", "SMLH","LUDO", "CUSACK", "EMO", "HMATRONABanner", "HDIANE", "KOF"])
    d={}
    out = []
    if arg1 == "list":
      n = 10
      final = [banner_list[i * n:(i + 1) * n] for i in range((len(banner_list) + n - 1) // n )]
      for i in range(len(final)):
        d["Page{0}".format(i+1)] = "\n".join(final[i])
      for page in list(d.keys()):
        out.append(discord.Embed(title="Banner list:",description=d[page], color=ctx.author.color))
      if len(final) == 1:
        em = discord.Embed(title="Banner list:",description=d['Page1'], color=ctx.author.color)
        return await ctx.send(embed=em)
      paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
      paginator.add_reaction('⏮️', "first")
      paginator.add_reaction('⏪', "back")
      paginator.add_reaction('🔐', "lock")
      paginator.add_reaction('⏩', "next")
      paginator.add_reaction('⏭️', "last")
      embeds = out
      return await paginator.run(embeds)
    if arg1.upper() not in banner_list:
      em = discord.Embed(description = 'There is no such banner', color = discord.Color.red())
      return await ctx.send(embed = em)
    else:
      arg = arg1.upper()

    banner = str(arg.upper()) + "Banner"
    all_units = []
    path = f".//Banner//{banner}"
    files = os.listdir(path)
    for unit in files:
      image = path+"//"+str(unit)
      all_units.append(image)
    n = 5
    split_units = [all_units[i * n:(i + 1) * n] for i in range((len(all_units) + n - 1) // n )]    
    part = 0
    for section in split_units:
      if len(section) == 5:
        im0 = Image.open(section[0])
        im1 = Image.open(section[1])
        im2 = Image.open(section[2])
        im3 = Image.open(section[3])
        im4 = Image.open(section[4])
        get_concat_h_multi_blank([im0,im1,im2,im3,im4]).save(f'.//Banner//pull//{ID}{part}.jpg')
        part+=1
      else:
        try:
          im0 = Image.open(section[0])
        except:
          im0 = Image.new("RGB", (100, 100), (47,49,54))
        try:
          im1 = Image.open(section[1])
        except:
          im1 = Image.new("RGB", (100, 100), (47,49,54))
        try:
          im2 = Image.open(section[2])
        except:
          im2 = Image.new("RGB", (100, 100), (47,49,54))
        try:
          im3 = Image.open(section[3])
        except:
          im3 = Image.new("RGB", (100, 100), (47,49,54))
        try:
          im4 = Image.open(section[4])
        except:
          im4 = Image.new("RGB", (100, 100), (47,49,54))
        get_concat_h_multi_blank([im0,im1,im2,im3,im4]).save(f'.//Banner//pull//{ID}{part}.jpg')

    images = list(os.listdir(".//Banner//pull"))
    Image.open(f".//Banner//pull//{images[0]}").save(f'.//Banner//pull//{ID}.jpg')
    images.pop(0)
    for unit in images:
      img = Image.open(f'.//Banner//pull//{ID}.jpg')
      addon = Image.open(f".//Banner//pull//{unit}")
      get_concat_v_blank(img, addon).save(f'.//Banner//pull//{ID}.jpg')

    quote = f"{arg.upper()} Banner contain"
    file = discord.File(f'.//Banner//pull//{ID}.jpg')
    em = discord.Embed(title = quote, colour = ctx.author.color)
    em.set_footer(text=f"use <{ctx.prefix}banner list> to check available banners")
    em.set_image(url = f"attachment://{ID}.jpg")
    await ctx.send(embed = em, file = file)

    try:
      shutil.rmtree('.//Banner//pull//')
    except OSError as e:
      print("Error: %s : %s" % ('.//Banner//pull//', e.strerror))
    return os.mkdir('.//Banner//pull//')


  @commands.command(aliases = ['+gc','++'])
  @commands.has_any_role('ADMIN','N⍧ Sovereign', 'G⍧ Archangels', 'K⍧ Kage', 'le vendel' , 'D⍧ Dragon', 'W⍧ Grace', 'R⍧ Leviathan', 'Overseer')
  async def add_gc(self,ctx,unit):
    """ Add a GC note for reference """
    def check(m):
      return m.author == ctx.author and m.channel == ctx.message.channel
    with open("sdsgc.json", "r") as f:
      notes = json.load(f)
    tag = unit
    if str(tag) not in notes:
      notes[str(tag)] = {}
    em = discord.Embed(description = f'What is the full name of the unit of this tag?', colour = ctx.author.color)
    await ctx.send(embed = em)
    try:
      msg1 = await self.client.wait_for("message",timeout= 60, check=check)
      unit_name = msg1.content
      em = discord.Embed(description = f'What is the reference for {unit_name}', colour = ctx.author.color)
      await ctx.send(embed = em)
      try:
        msg2 = await self.client.wait_for("message",timeout= 60, check=check)
        unit_ref = msg2.content
        notes[str(tag)][str(unit_name)] = unit_ref
        with open("sdsgc.json","w") as f:
            json.dump(notes,f,indent=4)
        em = discord.Embed(description=f"Note on {str(tag)} saved", colour = botcolour)
        return await ctx.send(embed = em)        
      except asyncio.TimeoutError:
        em = discord.Embed(description = f"You took too long... try again later when you are ready", colour = discord.Color.red())
        return await ctx.send(embed = em)
    except asyncio.TimeoutError:
      em = discord.Embed(description = f"You took too long... try again later when you are ready", colour = discord.Color.red())
      return await ctx.send(embed = em)


  @commands.command(aliases = ['?gc','??'])
  async def read_gc(self,ctx,unit="listing"):
    """ Refer to the unit's reference """
    with open("sdsgc.json", "r") as f:
      notes = json.load(f)
    nlist = sorted(list(notes))
    d = {}
    out = []
    if unit == "listing":
      n = 10
      final = [nlist[i * n:(i + 1) * n] for i in range((len(nlist) + n - 1) // n )]
      for i in range(len(final)):
        d["Page{0}".format(i+1)] = "\n".join(final[i])
      for page in list(d.keys()):
        out.append(discord.Embed(title="Unit list:",description=d[page], color=ctx.author.color))
      if len(final) == 1:
        em = discord.Embed(title="Unit list:",description=d['Page1'], color=ctx.author.color)
        return await ctx.send(embed=em)
      paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
      paginator.add_reaction('⏮️', "first")
      paginator.add_reaction('⏪', "back")
      paginator.add_reaction('🔐', "lock")
      paginator.add_reaction('⏩', "next")
      paginator.add_reaction('⏭️', "last")
      embeds = out
      return await paginator.run(embeds)
    tag = unit
    try:
      units = notes[str(tag)]
      for i in units:
        unit_name = i
        unit_ref = notes[str(tag)][unit_name]
        break
      em = discord.Embed(title=unit_name , description=unit_ref, colour = botcolour)
      return await ctx.send(embed = em)
    except:
      msg = f'There is no note on `{str(unit)}\n`'
      suggest = []
      for i in nlist:
        if tag.capitalize() in list(notes[i].keys())[0]:
          suggest.append([list(notes[i].keys())[0],i])
      if len(suggest) > 0:
        msg += '\n__Suggested:__'
        for item in suggest:
          msg += f'\n➣**{item[0]}**\n{ctx.prefix}?gc {item[1]}\n'
      em = discord.Embed(description=msg, colour = discord.Color.red())
      return await ctx.send(embed = em)

  @commands.command(aliases = ['-gc','--'])
  @commands.has_any_role('ADMIN','N⍧ Sovereign', 'G⍧ Archangels', 'K⍧ Kage', 'le vendel' , 'D⍧ Dragon', 'W⍧ Grace', 'R⍧ Leviathan', 'Overseer')
  async def remove_gc(self,ctx,unit="listing"):
    """ Remove the unit's reference """
    with open("sdsgc.json", "r") as f:
      notes = json.load(f)
    if unit == "listing":
      notelist = "Remove which one?"
      for item in notes:
        notelist+="\n➣"
        notelist+=str(item)
      notelist+=f"\nSend the command again with the unit ie. {ctx.prefix}{notes[0]}"
      return await ctx.send(notelist)
    tag = unit
    try:
      del notes[str(tag)]
      with open("sdsgc.json","w") as f:
          json.dump(notes,f,indent=4)
      em = discord.Embed(description=f"Note on {str(tag)} is removed", colour = botcolour)
      return await ctx.send(embed = em)
    except:
      em = discord.Embed(description=f"There is no note on `{str(tag)}`", color = discord.Color.red())
      return await ctx.send(embed = em)


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
    return os.remove(f'.//RSPVP//pull//{ctx.author.id}.jpg')

  @commands.command(aliases=['mp'])
  @commands.cooldown(1,5,commands.BucketType.user)
  async def multipull(self,ctx,times=1,banner=None):
    """ Pull on random banner a number of time """
    if int(times) > 10:
      times = int(10)
      await ctx.send(f'{ctx.author.mention} maximum of 10 multis at once')
    for i in range(int(times)):
      try:
        pending_command = self.client.get_command('pull')
        await ctx.invoke(pending_command,banner)
      except:
        return await ctx.send("Command Failed <@399558274753495040>")

  @commands.command(aliases = ['+e'])
  async def add_event(self,ctx,*,event):
    """ Add an event """
    def check(m):
      return m.author == ctx.author and m.channel == ctx.message.channel
    with open("event.json", "r") as f:
      notes = json.load(f)
    if '`' in event:
      return await ctx.send("No. Just no.")
    event_name = str(event)
    if str(event_name) not in notes:
      notes[str(event_name)] = {}
    em = discord.Embed(description = f'When does `{event_name}` START?', colour = ctx.author.color)
    await ctx.send(embed = em)
    try:
      msg1 = await self.client.wait_for("message",timeout= 60, check=check)
      event_start = msg1.content
      notes[str(event_name)]['START'] = event_start
      em = discord.Embed(description = f'When does `{event_name}` END?', colour = ctx.author.color)
      await ctx.send(embed = em)
      try:
        msg2 = await self.client.wait_for("message",timeout= 60, check=check)
        event_end = msg2.content
        notes[str(event_name)]['END'] = event_end
        with open("event.json","w") as f:
            json.dump(notes,f,indent=4)
        em = discord.Embed(description=f"Event on {str(event_name)} recorded", colour = botcolour)
        return await ctx.send(embed = em)        
      except asyncio.TimeoutError:
        em = discord.Embed(description = f"You took too long... try again later when you are ready", colour = discord.Color.red())
        return await ctx.send(embed = em)
    except asyncio.TimeoutError:
      em = discord.Embed(description = f"You took too long... try again later when you are ready", colour = discord.Color.red())
      return await ctx.send(embed = em)

  @commands.command()
  async def timenow(self,ctx):
    """ Display in game time """
    now = datetime.now(tz=tz.gettz("US/Pacific"))
    em = discord.Embed(description = now.strftime("%A, %B %d, %Y at %-I:%M %p %Z"), colour = discord.Color.greyple())
    await ctx.send(embed=em)

  @commands.command(aliases = ['events'])
  async def event(self,ctx):
    """ Display ongoing and upcoming events """
    def strfdelta(tdelta, fmt):
      d = {"days": tdelta.days}
      d["hours"], rem = divmod(tdelta.seconds, 3600)
      d["minutes"], d["seconds"] = divmod(rem, 60)
      return fmt.format(**d)

    with open("event.json", "r") as f:
      main = json.load(f)
    events = dict(main)
    now = datetime.now(tz=tz.gettz("US/Pacific"))
    ongoing = "```diff\n"
    upcoming = "```diff\n"
    for event in events:
      start_date = parser.parse(events[event]["START"])
      end_date = parser.parse(events[event]["END"])
      start_date = start_date.replace(tzinfo=tz.gettz("US/Pacific"))
      end_date = end_date.replace(tzinfo=tz.gettz("US/Pacific"))
      starting = start_date - now
      ending = end_date - now
      if ending.days <0:
        del main[event]
      if starting.days < 0: #event started
        countdown = strfdelta(ending,"{days}d{hours}h{minutes}m")
        end_date = end_date.strftime("%d %b %Y %I:%M %p")
        ongoing += f"\n{event}\n+ End : {end_date} ({countdown})"
      else:
        countdown = strfdelta(starting,"{days}d{hours}h{minutes}m")
        start_date = start_date.strftime("%d %b %Y %-I:%M %p")
        upcoming += f"\n{event}\n+ Start : {start_date} ({countdown})"
    ongoing += "```"
    upcoming += "```"
    if ongoing == "```diff\n```":
      ongoing = "```No ongoing event```"
    if upcoming == "```diff\n```":
      upcoming = "```No upcoming event```"
    embed=discord.Embed(color=discord.Color.purple())
    embed.add_field(name="Ongoing Events", value=ongoing, inline=False)
    embed.add_field(name="Upcoming Events", value=upcoming, inline=False)
    with open("event.json","w") as f:
      json.dump(main,f,indent=4)
    return await ctx.send(embed=embed)
        
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

def get_concat_v_resize(im1, im2, resample=Image.BICUBIC, resize_big_image=True):
    if im1.width == im2.width:
        _im1 = im1
        _im2 = im2
    elif (((im1.width > im2.width) and resize_big_image) or
          ((im1.width < im2.width) and not resize_big_image)):
        _im1 = im1.resize((im2.width, int(im1.height * im2.width / im1.width)), resample=resample)
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((im1.width, int(im2.height * im1.width / im2.width)), resample=resample)
    dst = Image.new('RGB', (_im1.width, _im1.height + _im2.height))
    dst.paste(_im1, (0, 0))
    dst.paste(_im2, (0, _im1.height))
    return dst

def get_concat_tile_resize(im_list_2d, resample=Image.BICUBIC):
    im_list_v = [get_concat_h_multi_resize(im_list_h, resample=resample) for im_list_h in im_list_2d]
    return get_concat_v_multi_resize(im_list_v, resample=resample)

def setup(client):
  client.add_cog(SDSGC(client))