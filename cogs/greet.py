import discord, os, random, requests, json, pymongo, asyncio
from discord.ext import commands,tasks
from pymongo import MongoClient
from html import unescape

cluster = MongoClient(os.getenv('MONGODB'))

db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]
liveness = db["liveness"]
mon = liveness.find_one({"setting":"main"})

def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
botcolour = 0x0fa4aab

mc_channels = [851668288391872572,851665369726320641]



with open("active.json", 'r') as f:
  activedata = json.load(f)
  f.close()

class Greetings(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.keepactive.start()

    @tasks.loop(minutes=555)
    async def keepactive(self):
      if mon["liveness"] == True:
        try:
          channel = await self.client.fetch_channel(516246018988441602)
          member = random.choice(mon["people"])
          quote = f"{member} "
          apiresult = apicall()
          quote += apiresult
          return await channel.send(quote)
        except:
          print("smth wrong")

    @keepactive.before_loop
    async def before_keepactive(self):
      await self.client.wait_until_ready()

    @commands.command()
    async def liveness(self,ctx, ping="False"):
      if ping == "-t":
        channel = await self.client.fetch_channel(516246018988441602)
        member = random.choice(mon["people"])
        quote = f"{member} "
        apiresult = apicall()
        quote += apiresult
        return await channel.send(quote)
      else:
        await ctx.send(apicall())

    @commands.command()
    @commands.has_any_role('ADMIN','N⍧ Sovereign', 'le vendel' , 'G⍧ Archangels', 'K⍧ Kage', 'D⍧ Dragon', 'W⍧ Grace', 'R⍧ Leviathan')
    async def umc(self,ctx):
      """ Update member count """
      for channel_id in mc_channels:
        try:
          channel = await self.client.fetch_channel(channel_id)
          member_count = channel.guild.member_count
          await channel.edit(name=f'Members: {member_count}')
        except:
          pass
      return await ctx.send("Member count updated")

    @commands.command()
    @commands.has_any_role('ADMIN','N⍧ Sovereign', 'le vendel' , 'G⍧ Archangels', 'K⍧ Kage', 'D⍧ Dragon', 'W⍧ Grace', 'R⍧ Leviathan')
    async def edit_welcome(self,ctx):
      """ Edit welcome message """
      def check(m):
        return m.author == ctx.author and m.channel == ctx.message.channel
      user = ctx.author
      with open("greet.json", "r") as f:
        notes = json.load(f)
      if str(user.guild.id) not in notes:
        notes[str(user.guild.id)] = {}
        # add new welcome
        em = discord.Embed(description = f'What is the welcome message?', colour = ctx.author.color)
        await ctx.send(embed = em)
        try:
          msg1 = await self.client.wait_for("message",timeout= 60, check=check)
          welcome_msg = msg1.content
          notes[str(user.guild.id)]['WELCOME'] = welcome_msg
          with open("greet.json","w") as f:
            json.dump(notes,f,indent=4)
          em = discord.Embed(description="Welcome message has been set", colour = botcolour)
          return await ctx.send(embed = em)    
        except asyncio.TimeoutError:
          em = discord.Embed(description = f"You took too long... try again later when you are ready", colour = discord.Color.red())
          return await ctx.send(embed = em)
      # send current and then wait for update
      em = discord.Embed(description = notes[str(user.guild.id)]['WELCOME'], colour = botcolour)
      await ctx.send(content ="Current welcome message is below, send the updated one within 60s to update it", embed = em)
      try:
        msg1 = await self.client.wait_for("message",timeout= 60, check=check)
        if msg1.content == 'cancel':
          return await ctx.send("Okay")
        welcome_msg = msg1.content
        notes[str(user.guild.id)]['WELCOME'] = welcome_msg
        with open("greet.json","w") as f:
          json.dump(notes,f,indent=4)
        em = discord.Embed(description="New welcome message has been set", colour = botcolour)
        return await ctx.send(embed = em)    
      except asyncio.TimeoutError:
        em = discord.Embed(description = f"You took too long... try again later when you are ready", colour = discord.Color.red())
        return await ctx.send(embed = em)


    @commands.Cog.listener()
    async def on_member_join(self, member):
      with open("greet.json", "r") as f:
        notes = json.load(f)
      if member.guild.id == 825583328111230977:
        channel = member.guild.system_channel
        if channel is not None:
          msg = f"<a:welcome:853659229607690270> Welcome to {member.guild} {member.mention} <a:welcome:853659229607690270>"
          em= discord.Embed(description=notes[str(member.guild.id)]['WELCOME'],colour = botcolour)
          return await channel.send(content = msg, embed=em)

      elif member.guild.id == 692808940190433360:
        channel = member.guild.system_channel
        if channel is not None:
          msg = f"<a:welcome:853659229607690270> Welcome to Null Community {member.mention} <a:welcome:853659229607690270>"
          em= discord.Embed(description=notes[str(member.guild.id)]['WELCOME'],colour = botcolour)
          return await channel.send(content = msg, embed=em)

def apicall():
  temp = random.randrange(2)
  quote = ""
  if temp == 0:
    roll = random.randrange(1,6)
    for i in range(roll):
      catid = random.choice(mon["category"])
      difficulty = mon["difficulty"]
      qntype = mon["type"]
      url = f"https://opentdb.com/api.php?amount=1&category={catid}&difficulty={difficulty}&type={qntype}"
      r = requests.request("GET", url).json()
      category = unescape(r['results'][0]['category'])
      diff = unescape(r['results'][0]['difficulty'])
      question = unescape(r['results'][0]['question'])
      ans = unescape(r['results'][0]['correct_answer'])
      options = [ans] + unescape(r['results'][0]['incorrect_answers'])
      options = "` or `".join(random.sample(options, len(options)))
      quote += f"\n{i+1}. Category: {category} Difficulty: {diff.upper()}\n{question}\n`{options}`\nAnswer: ||`{ans}`||\n"
    return quote
  else:
    url = mon["jokeapiurl"]
    r = requests.request("GET", url).json()
    jokes = r['jokes']
    for i in range(r['amount']):
        category=jokes[i]['category']
        typing=jokes[i]['type']
        if typing == "single":
            joke=jokes[i]['joke']
            quote += f"\n{i+1}. Category: {category} Joke\n{joke}\n"
        elif typing == "twopart":
            setup=jokes[i]['setup']
            delivery=jokes[i]['delivery']
            quote += f"\n{i+1}. Category: {category} Joke\n{setup}\n||{delivery}||\n"
    return quote



def setup(client):
  client.add_cog(Greetings(client))
