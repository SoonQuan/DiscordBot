import discord, os, shutil, json, re, asyncio, random, DiscordUtils
from discord.ext import commands
from pymongo import MongoClient
from PIL import Image
from datetime import datetime
from dateutil import parser, tz

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]
sdsgc = db["sdsgcProfile"]

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
  commands.globalcount = 0 

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
    banner_list = sorted(["T1","VAL","AM","DZ","MERLIN","FZEL", "REZERO", "ST", "EXARTH", "FBAN", "FGOW", "FKING", "DMELI", "SARIEL", "HAWK","SEASON", "RAG1", "RAG2", "RAG3", "RAG4", "SROXY","SMLH", "LUDO", "CUSACK", "EMO", "HMATRONA", "MELA", "HDIANE", "XLILLIA", "XLIZ", "KOF"])
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
    ban4p = ["T1","AM","MERLIN","FZEL","FBAN","LUDO", "CUSACK", "FGOW", "FKING", "DMELI"]
    ban3p = ["VAL","REZERO","ST","EXARTH","HAWK", "SARIEL","SEASON", "RAG1", "RAG2", "RAG3", "RAG4", "SROXY", "SMLH", "EMO", "HMATRONA", "MELA", "HDIANE", "XLILLIA", "XLIZ", "KOF"]

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

  @commands.command(aliases=['banners'])
  @commands.cooldown(1,1,commands.BucketType.user)
  async def banner(self,ctx,arg1="list"):
    """ Check the banner listed """
    user = ctx.author
    await open_account(user)
    await open_server(user)
    users = mainbank.find_one( {'_id':user.id} )
    ID = users["_id"]

    banner_list = sorted(["T1","VAL","AM","DZ","MERLIN","FZEL", "REZERO", "ST", "EXARTH","FBAN", "FGOW", "FKING", "DMELI", "SARIEL","HAWK","SEASON", "RAG1", "RAG2", "RAG3", "RAG4", "SROXY", "SMLH","LUDO", "CUSACK", "EMO", "HMATRONA", "MELA", "HDIANE", "XLILLIA", "XLIZ", "KOF"])
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


  @commands.command()
  @commands.cooldown(1,1,commands.BucketType.user)
  async def rselectpvp(self,ctx):
    """ Randomly select 4 units for you """
    names = ctx.author.display_name
    user = sdsgc.find_one( {'_id': "BASE"} )
    allunits = []
    for key in user:
      if type(user[key]) == dict:
        if user[key]['owned'] == True:
          allunits.append(user[key]["directory"])
    dirs = []
    while len(dirs)<4:
      image = random.choice(allunits)
      path = image.split('/')[-2]
      if len(dirs) == 0:
        dirs.append(image)
      else:
        copy = 0
        for item in dirs:
          if str(path) in str(item):
            copy+=1
            break
          elif 'Hawk' in image and 'Hawk' in str(item):
            copy+=1
            break
        if copy>0:
          continue
        else:
          dirs.append(image)
    random.shuffle(dirs)
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



  @commands.command(aliases=['rspvp', 'rs'])
  @commands.cooldown(1,1,commands.BucketType.user)
  async def randomselect(self,ctx,*,exclude:str=""):
    """ Randomly select 4 units for you with exclude list"""
    # if ctx.author.id == 308042980944642050 or ctx.author.id == 303066334038720516 or ctx.author.id == 131232317518774272:
    #   quote = "Liz for you"
    #   file = discord.File(f'.//RSPVP//KAI.jpg',filename="image.jpg")
    #   embed = discord.Embed(title = quote,colour = ctx.author.color)
    #   embed.set_image(url = f"attachment://image.jpg")
    #   embed.set_thumbnail(url=ctx.author.avatar_url)
    #   return await ctx.send(embed = embed, file = file)
    names = ctx.author.display_name
    user = sdsgc.find_one( {'_id': ctx.author.id} )
    if user == None:
      pending_command = self.client.get_command('createProfile')
      await ctx.invoke(pending_command)
      user = sdsgc.find_one( {'_id': ctx.author.id} )
    allunits = []
    for key in user:
      if type(user[key]) == dict:
        if user[key]['owned'] == True:
          allunits.append(user[key]["directory"])
    allunits.sort()
    try:
      tries = 0
      if exclude == "":
        pending_command = self.client.get_command('rselectpvp')
        await ctx.invoke(pending_command)
      elif exclude.endswith(' only'):
        excludelist = exclude.lower().split(' ')
        # print(excludelist)
        includelist = excludelist[0:-1]
        dirs = []
        while len(dirs)<4 and tries < 500:
          tries += 1
          ban = True
          image = random.choice(allunits)
          path = image.split('/')[-2]
          # print(image)
          for include in includelist:
            if include in image.lower():
              # print('ONLY UNIT')
              ban = False
          if ban == False:
            if len(dirs) == 0:
              dirs.append(image)
            else:
              copy = 0
              for item in dirs:
                if str(path) in str(item):
                  copy+=1
                  break
                elif 'Hawk' in image and 'Hawk' in str(item):
                  copy+=1
                  break
              if copy>0:
                continue
              else:
                dirs.append(image)
        random.shuffle(dirs)
        im0 = Image.open(dirs[0])
        im1 = Image.open(dirs[1])
        im2 = Image.open(dirs[2])
        im3 = Image.open(dirs[3])

        get_concat_h_multi_blank([im0,im1,im2,im3]).save(f'.//RSPVP//pull//{ctx.author.id}.jpg')
        quote = f"{names} randomly selected units\nFrom:\n"
        for x in exclude.split(' '):
          quote += f"➣{str(x)} "
        file = discord.File(f'.//RSPVP//pull//{ctx.author.id}.jpg')
        embed = discord.Embed(title = quote,colour = ctx.author.color)
        embed.set_image(url = f"attachment://{ctx.author.id}.jpg")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.send(embed = embed, file = file)
        return os.remove(f'.//RSPVP//pull//{ctx.author.id}.jpg')
      elif "(" in exclude:
        dirs = []
        unitNum = 4
        forcedUnits = re.search(r"\(([A-Za-z0-9_ ,-]+)\)", exclude)
        excludeList = re.sub(r"\(([A-Za-z0-9_ ,-]+)\)", "",exclude).lower().split(' ')
        forcedList = forcedUnits.group(0)[1:-1].split(',')
        excludeList = list(map(str.strip, excludeList))
        forcedList = list(map(str.strip, forcedList))
        excludeList = [x for x in excludeList if x]
        forcedList = [x for x in forcedList if x]
        for include in forcedList:
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
            dirs.append(filterUnit[0])
            unitNum-=1
        while unitNum > 0:
          ban = False
          image = random.choice(allunits)
          path = image.split('/')[-2]
          # print(image)
          for ex in excludeList:
            if ex in image.lower():
              # print('BAN UNIT')
              ban = True
          if ban == False:
            if len(dirs) == 0:
              dirs.append(image)
              unitNum-=1
            else:
              copy = 0
              for item in dirs:
                if str(path) in str(item):
                  copy+=1
                  break
                elif 'Hawk' in image and 'Hawk' in str(item):
                  copy+=1
                  break
              if copy>0:
                continue
              else:
                dirs.append(image)
                unitNum-=1
        random.shuffle(dirs)
        im0 = Image.open(dirs[0])
        im1 = Image.open(dirs[1])
        im2 = Image.open(dirs[2])
        im3 = Image.open(dirs[3])

        get_concat_h_multi_blank([im0,im1,im2,im3]).save(f'.//RSPVP//pull//{ctx.author.id}.jpg')
        quote = f"{names} selected:\n"
        for x in forcedList:
          quote += f"➣{str(x)} "
        quote += "\nAnd randomly selected units"
        if len(excludeList) != 0:
          quote += "\nExcluding:\n"
          for x in excludeList:
            quote += f"➣{str(x)} "
        file = discord.File(f'.//RSPVP//pull//{ctx.author.id}.jpg')
        embed = discord.Embed(title = quote,colour = ctx.author.color)
        embed.set_image(url = f"attachment://{ctx.author.id}.jpg")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.send(embed = embed, file = file)
        return os.remove(f'.//RSPVP//pull//{ctx.author.id}.jpg')
      elif "[" in exclude:
        dirs = []
        unitNum = 4
        allrank = ['-ssr', '-sr', '-r']
        limits = re.search(r"\[([A-Za-z0-9_ ,-]+)\]", exclude)
        excludeList = re.sub(r"\[([A-Za-z0-9_ ,-]+)\]", "",exclude).lower().split(' ')
        limitsList = limits.group(0)[1:-1].split(',')
        excludeList = list(map(str.strip, excludeList))
        limitsList = list(map(str.strip, limitsList))
        excludeList = [x for x in excludeList if x]
        limitsList = [x for x in limitsList if x]
        filterUnits = allunits
        for ex in excludeList:
          filterUnits = list(filter(lambda k: ex not in k.lower(), filterUnits))
        for limit in limitsList:
          includelist = limit.lower().split(' ') #['1', 'SSR']
          numb = int(includelist[0])
          rank = '-'+ str(includelist[1]).lower() #'-ssr'
          try:
            allrank.remove(rank)
          except:
            embed = discord.Embed(title=f"Input error", description=f"Correct example: `[1 ssr, 1 sr, 2 r]`", colour = discord.Color.red())
            return await ctx.send(embed = embed)
          while numb > 0 and tries < 500:
            tries += 1
            ban = False
            image = random.choice(filterUnits)
            path = image.split('/')[-2]
            # print(image)
            if rank == '-ssr':
              for rk in allrank:
                if rk in image.lower():
                  # print(f'unit with {rank}')
                  ban = True
            else:
              if rank not in image.lower():
                # print(f'unit with {rank}')
                ban = True
            if ban == False:
              if len(dirs) == 0:
                dirs.append(image)
                numb-=1
                unitNum-=1
              else:
                copy = 0
                for item in dirs:
                  if str(path) in str(item):
                    copy+=1
                    break
                  elif 'Hawk' in image and 'Hawk' in str(item):
                    copy+=1
                    break
                if copy>0:
                  continue
                else:
                  dirs.append(image)
                  numb-=1
                  unitNum-=1
        while unitNum > 0:
          ban = True
          image = random.choice(filterUnits)
          path = image.split('/')[-2]
          # print(image)
          for ex in allrank:
            if ex in image.lower():
              # print('BAN UNIT')
              ban = False
          if ban == False:
            if len(dirs) == 0:
              dirs.append(image)
              unitNum-=1
            else:
              copy = 0
              for item in dirs:
                if str(path) in str(item):
                  copy+=1
                  break
                elif 'Hawk' in image and 'Hawk' in str(item):
                  copy+=1
                  break
              if copy>0:
                continue
              else:
                dirs.append(image)
                unitNum-=1
        random.shuffle(dirs)
        im0 = Image.open(dirs[0])
        im1 = Image.open(dirs[1])
        im2 = Image.open(dirs[2])
        im3 = Image.open(dirs[3])

        get_concat_h_multi_blank([im0,im1,im2,im3]).save(f'.//RSPVP//pull//{ctx.author.id}.jpg')
        quote = f"{names} selected:\n"
        for x in limitsList:
          quote += f"➣{str(x).upper()} Limit "
        quote += "\nAnd randomly selected units"
        if len(excludeList) != 0:
          quote += "\nExcluding:\n"
          for x in excludeList:
            quote += f"➣{str(x)} "
        file = discord.File(f'.//RSPVP//pull//{ctx.author.id}.jpg')
        embed = discord.Embed(title = quote,colour = ctx.author.color)
        embed.set_image(url = f"attachment://{ctx.author.id}.jpg")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.send(embed = embed, file = file)
        return os.remove(f'.//RSPVP//pull//{ctx.author.id}.jpg')
      else:
        excludelist = exclude.lower().split(' ')
        # print(excludelist)
        dirs = []
        while len(dirs)<4 and tries < 500:
          tries += 1
          ban = False
          image = random.choice(allunits)
          path = image.split('/')[-2]
          # print(image)
          for ex in excludelist:
            if ex in image.lower():
              # print('BAN UNIT')
              ban = True
          if ban == False:
            if len(dirs) == 0:
              dirs.append(image)
            else:
              copy = 0
              for item in dirs:
                if str(path) in str(item):
                  copy+=1
                  break
                elif 'Hawk' in image and 'Hawk' in str(item):
                  copy+=1
                  break
              if copy>0:
                continue
              else:
                dirs.append(image)
        random.shuffle(dirs)
        im0 = Image.open(dirs[0])
        im1 = Image.open(dirs[1])
        im2 = Image.open(dirs[2])
        im3 = Image.open(dirs[3])

        get_concat_h_multi_blank([im0,im1,im2,im3]).save(f'.//RSPVP//pull//{ctx.author.id}.jpg')
        quote = f"{names} randomly selected units\nExcluding:\n"
        for x in exclude.split(' '):
          quote += f"➣{str(x)} "
        file = discord.File(f'.//RSPVP//pull//{ctx.author.id}.jpg')
        embed = discord.Embed(title = quote,colour = ctx.author.color)
        embed.set_image(url = f"attachment://{ctx.author.id}.jpg")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.send(embed = embed, file = file)
        return os.remove(f'.//RSPVP//pull//{ctx.author.id}.jpg')
    except IndexError:
      quote = "Please use a wider range of units\nBut sure I got you <:stares:887196954017296436>"
      standard = "Please use a wider range of units <:stares:887196954017296436>"
      main = discord.Embed(title = standard,colour = discord.Color.red())
      main.set_footer(text= f"try {ctx.prefix}c <unit name>")
      embed = discord.Embed(title = quote,colour = discord.Color.red())
      embed.set_footer(text= f"try {ctx.prefix}c <unit name>")
      quote1 = "Here you go"
      embed2 = discord.Embed(description = quote1,colour = discord.Color.red())
      embed2.set_footer(text= f"try {ctx.prefix}c <unit name>")
      num = random.randrange(100)
      if num < 10 or commands.globalcount >= 3:
        commands.globalcount = 0
        MSG = await ctx.send(embed = embed)
        await asyncio.sleep(3)
        await MSG.edit(embed=embed2)
        await asyncio.sleep(3)
        await MSG.delete()
        return await ctx.send("https://tenor.com/view/rick-rickroll-jebaited-meme-got-em-gif-17877057")
      elif num < 20: 
        file = discord.File(f'.//RSPVP//unit.png', filename="image.jpg")
        main = discord.Embed(title = "Please use a wider range of units",colour = discord.Color.red())
        main.set_image(url = f"attachment://image.jpg")
        main.set_footer(text= f"try {ctx.prefix}c <unit name>")
        return await ctx.send(embed = main, file=file)
      else:
        commands.globalcount += 1
        return await ctx.send(embed = main)

  @commands.command(aliases=['c'])
  @commands.cooldown(1,1,commands.BucketType.user)
  async def character(self,ctx,*,include:str=""):
    """Show the image of the character """
    try:
      if include == "":
        em = discord.Embed(description = f'Please provide a character', colour = ctx.author.color)
        await ctx.send(embed=em)
      else:
        includelist = include.lower().split(' ')
        # print(includelist)
        allunits = []
        for base, dirs, files in os.walk(".//RSPVP//rspvp"):
            for file in files:
              allunits.append(str(os.path.join(base,file)))
        for i in includelist:
          allunits = list(filter(lambda k: i in k.lower(), allunits))

        n = 5
        split_units = [allunits[i * n:(i + 1) * n] for i in range((len(allunits) + n - 1) // n )]
        part = 0
        for section in split_units:
          if len(section) == 5:
            im0 = Image.open(section[0])
            im1 = Image.open(section[1])
            im2 = Image.open(section[2])
            im3 = Image.open(section[3])
            im4 = Image.open(section[4])
            get_concat_h_multi_blank([im0,im1,im2,im3,im4]).save(f'.//Banner//pull//{ctx.author.id}{part}.jpg')
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
            get_concat_h_multi_blank([im0,im1,im2,im3,im4]).save(f'.//Banner//pull//{ctx.author.id}{part}.jpg')

        images = list(os.listdir(".//Banner//pull"))
        Image.open(f".//Banner//pull//{images[0]}").save(f'.//Banner//pull//{ctx.author.id}.jpg')
        images.pop(0)
        for unit in images:
          img = Image.open(f'.//Banner//pull//{ctx.author.id}.jpg')
          addon = Image.open(f".//Banner//pull//{unit}")
          get_concat_v_blank(img, addon).save(f'.//Banner//pull//{ctx.author.id}.jpg')

        quote = include.upper()
        file = discord.File(f'.//Banner//pull//{ctx.author.id}.jpg', filename="image.jpg")
        em = discord.Embed(title = quote, colour = ctx.author.color)
        em.set_image(url = f"attachment://image.jpg")
        await ctx.send(embed = em,file=file)

        try:
          shutil.rmtree('.//Banner//pull//')
        except OSError as e:
          print("Error: %s : %s" % ('.//Banner//pull//', e.strerror))
        return os.mkdir('.//Banner//pull//')
    except IndexError:
      file = discord.File(f'.//RSPVP//questionmark.png', filename="image.jpg")
      embed = discord.Embed(title=f"No {include.upper()} found", colour = discord.Color.red())
      embed.set_image(url = f"attachment://image.jpg")
      return await ctx.send(embed = embed, file=file)

  @commands.command()
  @commands.cooldown(1,1,commands.BucketType.user)
  async def team(self,ctx,*,team:str=""):
    """Show the image of the character """
    names = ctx.author.display_name
    tempunit = ".//RSPVP//unit.png"
    selectedUnit = [tempunit,tempunit,tempunit,tempunit]
    quote = f"{names} has mentioned the following team\n"
    try:
      if team != "":
        teamlist = team.lower().split(',')
        print(teamlist)
        index=0
        for include in teamlist:
          includelist = include.lower().split(' ')
          filterUnit = []
          for base, dirs, files in os.walk(".//RSPVP//rspvp"):
              for file in files:
                filterUnit.append(str(os.path.join(base,file)))
          for i in includelist:
            filterUnit = list(filter(lambda k: i in k.lower(), filterUnit))
          if len(filterUnit) > 1:
            embed = discord.Embed(title=f"More than one {include.upper()} found", description="Please be more specific", colour = discord.Color.red())
            return await ctx.send(embed = embed)
          else:
            selectedUnit[index] = filterUnit[0]
            index+=1
        im0 = Image.open(selectedUnit[0])
        im1 = Image.open(selectedUnit[1])
        im2 = Image.open(selectedUnit[2])
        im3 = Image.open(selectedUnit[3])

        get_concat_h_multi_blank([im0,im1,im2,im3]).save(f'.//RSPVP//pull//{ctx.author.id}.jpg')
        
        file = discord.File(f'.//RSPVP//pull//{ctx.author.id}.jpg')
        embed = discord.Embed(title = quote,colour = ctx.author.color)
        embed.set_image(url = f"attachment://{ctx.author.id}.jpg")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.send(embed = embed, file = file)
        return os.remove(f'.//RSPVP//pull//{ctx.author.id}.jpg')
      else:
        em = discord.Embed(description = f'Please provide a team such as:\n{ctx.prefix}team Traitor Meli, hgowther, G brynhildr, hmatrona', colour = ctx.author.color)
        await ctx.send(embed=em)

    except IndexError:
      embed = discord.Embed(title=f"No {include.upper()} found", colour = discord.Color.red())
      return await ctx.send(embed = embed)

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

  # Random select profile 
  @commands.command(aliases=['missing'])
  async def profile(self, ctx, member:discord.Member=None):
    """ Display the missing units """
    if member == None:
      target = ctx.author
    else:
      target = member
    names = target.display_name
    user = sdsgc.find_one( {'_id': target.id} )
    if user == None:
      pending_command = self.client.get_command('createProfile')
      await ctx.invoke(pending_command)
      user = sdsgc.find_one( {'_id': target.id} )
    allunits = []
    for key in user:
      if type(user[key]) == dict:
        if user[key]['owned'] == False:
          allunits.append(user[key]["directory"])
    allunits.sort()
    if len(allunits) == 0:
      embed = discord.Embed(description="No missing units")
      return await ctx.send(embed=embed)
    n = 5
    split_units = [allunits[i * n:(i + 1) * n] for i in range((len(allunits) + n - 1) // n )]
    part = 0
    for section in split_units:
      if len(section) == 5:
        im0 = Image.open(section[0])
        im1 = Image.open(section[1])
        im2 = Image.open(section[2])
        im3 = Image.open(section[3])
        im4 = Image.open(section[4])
        get_concat_h_multi_blank([im0,im1,im2,im3,im4]).save(f'.//Banner//pull//{ctx.author.id}{part}.jpg')
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
        get_concat_h_multi_blank([im0,im1,im2,im3,im4]).save(f'.//Banner//pull//{ctx.author.id}{part}.jpg')

    images = list(os.listdir(".//Banner//pull"))
    Image.open(f".//Banner//pull//{images[0]}").save(f'.//Banner//pull//{ctx.author.id}.jpg')
    images.pop(0)
    for unit in images:
      img = Image.open(f'.//Banner//pull//{ctx.author.id}.jpg')
      addon = Image.open(f".//Banner//pull//{unit}")
      get_concat_v_blank(img, addon).save(f'.//Banner//pull//{ctx.author.id}.jpg')

    quote = f"{names} is missing the following units"
    file = discord.File(f'.//Banner//pull//{ctx.author.id}.jpg', filename="image.jpg")
    em = discord.Embed(title = quote, colour = target.color)
    em.set_image(url = f"attachment://image.jpg")
    await ctx.send(embed = em,file=file)

    try:
      shutil.rmtree('.//Banner//pull//')
    except OSError as e:
      print("Error: %s : %s" % ('.//Banner//pull//', e.strerror))
    return os.mkdir('.//Banner//pull//')
    
  @commands.command()
  @commands.is_owner()
  async def newUnit(self, ctx, unit, directory):
    """ Add new unit into the all user pool """
    sdsgc.update({}, {"$set": {unit: {"directory": directory}, {"owned"}: False }})
    await ctx.send(f"New unit {unit} added to all")

  @commands.command()
  @commands.is_owner()
  async def newBase(self, ctx):
    """ Create a new base for others to clone """
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
    """ Delete profile """
    sdsgc.remove({"_id":ctx.author.id})
    return await ctx.send("Profile deleted")

  @commands.command()
  async def createProfile(self, ctx):
    """ Create a profile with all units owned """
    base = sdsgc.find_one( {'_id': "BASE"} )
    base["_id"] = ctx.author.id
    sdsgc.insert_one(base)
    return await ctx.send("New Profile Initiated")

  @commands.command()
  async def rssetting(self, ctx, *, msg):
    """ Set the random select range """
    user = sdsgc.find_one( {'_id': ctx.author.id} )
    if user == None:
      pending_command = self.client.get_command('createProfile')
      await ctx.invoke(pending_command)
      user = sdsgc.find_one( {'_id': ctx.author.id} )    
    sdsgc.update_one({"_id":ctx.author.id}, {"$set":{"rs_setting":msg}})
    return await ctx.send(f"Random select setting set to {msg}")

  @commands.command(aliases=["srs"])
  async def setrs(self, ctx):
    """ Randomly select units with pre-set range """
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

  @commands.command(aliases=["ru","remove","rm"])
  async def removeUnit(self, ctx, *, unitlist):
    """ Remove a unit from user pool """
    user = sdsgc.find_one( {'_id': ctx.author.id} )
    if user == None:
      pending_command = self.client.get_command('createProfile')
      await ctx.invoke(pending_command)
      user = sdsgc.find_one( {'_id': ctx.author.id} )
    unitlist = unitlist.lower().split(',')
    for include in unitlist:
      try:
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
          if '\\' in str(filterUnit[0]):
            unit = str(filterUnit[0]).split('\\')[-1][0:-4]
          else:
            unit = str(filterUnit[0]).split('/')[-1][0:-4]
          sdsgc.find_one_and_update({"_id":ctx.author.id}, {"$set":{f"{unit}.owned":False}})
          await ctx.send(f"`{unit}` has been removed from `{ctx.author.display_name}`'s pool")
      except IndexError:
        file = discord.File(f'.//RSPVP//questionmark.png', filename="image.jpg")
        embed = discord.Embed(title=f"No {include.upper()} found", colour = discord.Color.red())
        embed.set_image(url = f"attachment://image.jpg")
        return await ctx.send(embed = embed, file=file)


  @commands.command(aliases=["add","own"])
  async def addUnit(self, ctx, *, unitlist):
    """ Add a unit to user pool """
    user = sdsgc.find_one( {'_id': ctx.author.id} )
    if user == None:
      pending_command = self.client.get_command('createProfile')
      await ctx.invoke(pending_command)
      user = sdsgc.find_one( {'_id': ctx.author.id} )
    unitlist = unitlist.lower().split(',')
    for include in unitlist:
      try:
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
          if '\\' in str(filterUnit[0]):
            unit = str(filterUnit[0]).split('\\')[-1][0:-4]
          else:
            unit = str(filterUnit[0]).split('/')[-1][0:-4]
          sdsgc.find_one_and_update({"_id":ctx.author.id}, {"$set":{f"{unit}.owned":True}})
          await ctx.send(f"`{unit}` has been added to `{ctx.author.display_name}`'s pool")
      except IndexError:
        file = discord.File(f'.//RSPVP//questionmark.png', filename="image.jpg")
        embed = discord.Embed(title=f"No {include.upper()} found", colour = discord.Color.red())
        embed.set_image(url = f"attachment://image.jpg")
        return await ctx.send(embed = embed, file=file)

  @commands.command()
  @commands.is_owner()
  async def addNewUnit(self, ctx, name, direct):
    sdsgc.update_many(
      {},
      {'$set': {
            f'{name}': {
                'directory': f'{direct}', 
                'owned': False
            }
        }
    }, upsert=True, array_filters=None
    )
    await ctx.send(f"New unit `{name}` added with `{direct}`")

  @commands.command()
  @commands.is_owner()
  async def renameUnit(self, ctx, oldname, newname, newdirect):
    sdsgc.update_many(
      {},
      {'$set': {
            f'{oldname}.directory': f'{newdirect}'
        }}, upsert=True, array_filters=None
    )
    sdsgc.update_many(
      {},
      {
        '$rename': {
            f'{oldname}': f'{newname}'
        }
      }, upsert=True, array_filters=None
    )
    await ctx.send(f"Unit `{oldname}` renamed with `{newname}`\nDirectory renamed with `{newdirect}`")


  @commands.command()
  @commands.is_owner()
  async def rmUnit(self, ctx, name):
    sdsgc.update_many({}, {'$unset': { name: ""}}, upsert=True, array_filters=None)
    await ctx.send(f"Unit `{name}` removed")
    
  @commands.command()
  async def unit(self,ctx,unit="listing"):
    """ Refer to the units on bot """
    user = sdsgc.find_one( {'_id': "BASE"} )
    allunits = []
    for key in user:
      if type(user[key]) == dict:
        allunits.append(key)

    nlist = sorted(allunits)
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

    msg = f'You are looking for `{str(unit)}\n`'
    suggest = []
    for i in nlist:
      if unit in i.lower():
        suggest.append(i)
    if len(suggest) > 0:
      msg += '\n__Suggested:__'
      for item in suggest:
        msg += f'\n➣{item}'
    em = discord.Embed(description=msg, colour = discord.Color.red())
    return await ctx.send(embed = em)

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