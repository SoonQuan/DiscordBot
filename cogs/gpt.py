import os, discord, aiohttp, asyncio
from discord.ext import commands
import pymongo
from pymongo import MongoClient

cluster = MongoClient(os.getenv('MONGODB'))
gptapikey = os.getenv('GPTAPIKEY')
db = cluster["luckbot"]
mainbank = db["mainbank"]
settings = db["settings"]
liveness = db["liveness"]


def get_prefix(client, message):
  server = settings.find_one({"gid":message.guild.id})
  return server["prefix"]

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
botcolour = 0x0fa4aab

class CHATGPT(commands.Cog):
  """ GPT commands """
  def __init__(self,client):
    self.client = client

  @commands.command()
  @commands.has_any_role("SqChatGPT")
  async def gpt(self, ctx,*, prompt):
    mon = liveness.find_one({"setting":"main"})
    if mon["chatgptsetting"]["live"] == True:
      async with aiohttp.ClientSession() as session:
        payload = {
          "model": mon["chatgptsetting"]["model"],
          "prompt": prompt,
          "max_tokens": mon["chatgptsetting"]["max_token"],
          "temperature": mon["chatgptsetting"]["temperature"],
          "presence_penalty": mon["chatgptsetting"]["presence_penalty"],
          "frequency_penalty": mon["chatgptsetting"]["frequency_penalty"],
          "best_of": 1
        }
        headers = {"Authorization": f"Bearer {gptapikey}"}
        async with session.post("https://api.openai.com/v1/completions", json=payload, headers=headers) as res:
          response = await res.json()
          print(response)
          if "error" in response:
            embed = discord.Embed(title="ChatGPT", description=response["error"]["message"], colour = ctx.author.color)
            await ctx.reply(embed=embed)
          else:
            embed = discord.Embed(title="ChatGPT", description=response["choices"][0]["text"], colour = ctx.author.color)
            footer = "Token Usage: " + str(response["usage"]["total_tokens"])
            embed.set_footer(text=footer)
            await ctx.reply(embed=embed)

  @commands.command()
  @commands.has_any_role("SqChatGPT")
  async def chat(self, ctx,*, prompt):
    mon = liveness.find_one({"setting":"main"})
    if mon["chatgptsetting"]["live"] == True:
      async with aiohttp.ClientSession() as session:
        payload = {
          "model": mon["chatgptsetting"]["chatmodel"],
          "messages": [{"role": "user", "content": prompt}]
        }
        headers = {"Authorization": f"Bearer {gptapikey}"}
        async with session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers) as res:
          response = await res.json()
          print(response)
          if "error" in response:
            embed = discord.Embed(title="ChatGPT", description=response["error"]["message"], colour = ctx.author.color)
            await ctx.reply(embed=embed)
          else:
            embed = discord.Embed(title="ChatGPT", description=response["choices"][0]["message"]["content"], colour = ctx.author.color)
            footer = "Token Usage: " + str(response["usage"]["total_tokens"])
            embed.set_footer(text=footer)
            await ctx.reply(embed=embed)

  @commands.command()
  @commands.has_any_role("SqChatGPT")
  async def chat2(self, ctx):
    mon = liveness.find_one({"setting":"main"})
    def check(m):
      return m.channel == ctx.message.channel and m.author.id == ctx.author.id
    if mon["chatgptsetting"]["live"] == True:
      system = mon["chatgptsetting"]["system"]
      chatRecords = [{"role": "system", "content": system}]
      initial = discord.Embed(description = f"Chat starting using system: `{system}`\nSend prompt within 30s to chat", colour = ctx.author.color)
      await ctx.reply(embed = initial)
      while len(chatRecords)<10:
        try:
          messagePrompt = await self.client.wait_for("message",timeout= 30, check=check)
          if messagePrompt.content.lower() == "stop":
            em1 = discord.Embed(description = "Nothing else for me? Alright have a good day.", colour = ctx.author.color)
            return await ctx.send(embed = em1)
          chatRecords.append({"role": "user", "content": messagePrompt.content})
          async with aiohttp.ClientSession() as session:
            payload = {
              "model": mon["chatgptsetting"]["chatmodel"],
              "messages": chatRecords
            }
            headers = {"Authorization": f"Bearer {gptapikey}"}
            async with session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers) as res:
              response = await res.json()
              print(response)
              if "error" in response:
                chatRecords.pop()
                embed = discord.Embed(title="ChatGPT", description=response["error"]["message"], colour = ctx.author.color)
                await ctx.reply(embed=embed)
              else:
                reply = response["choices"][0]["message"]["content"]
                embed = discord.Embed(title="ChatGPT", description=reply, colour = ctx.author.color)
                footer = "Token Usage: " + str(response["usage"]["total_tokens"])
                embed.set_footer(text=footer)
                chatRecords.append({"role": "assistant", "content": reply})
                await ctx.reply(embed=embed)
        except asyncio.TimeoutError: 
          em1 = discord.Embed(description = "Nothing else for me? Alright have a good day.", colour = ctx.author.color)
          return await ctx.reply(embed = em1)
      print(chatRecords)
      em1 = discord.Embed(description = "Enough for today. Have a good day." , colour = ctx.author.color)
      return await ctx.reply(embed = em1)

  @commands.command()
  @commands.has_any_role("SqChatGPT")
  async def setchat(self, ctx,*, prompt):
    mon = liveness.find_one({"setting":"main"})
    liveness.update_one({"setting":"main"}, {"$set":{f"chatgptsetting.system":str(prompt)}})
    embed = discord.Embed(title="ChatGPT Update", description=f"New System: {prompt}", colour = ctx.author.color)
    await ctx.reply(embed=embed)

  @commands.command()
  @commands.has_any_role("SqChatGPT")
  async def image(self, ctx,*, prompt):
    mon = liveness.find_one({"setting":"main"})
    if mon["chatgptsetting"]["live"] == True:
      async with aiohttp.ClientSession() as session:
        payload = {
          "prompt": prompt,
          "n": 2,
          "size": mon["chatgptsetting"]["imagesize"]
        }
        headers = {"Authorization": f"Bearer {gptapikey}"}
        async with session.post("https://api.openai.com/v1/images/generations", json=payload, headers=headers) as res:
          response = await res.json()
          print(response)
          if "error" in response:
            embed = discord.Embed(title="ChatGPT", description=response["error"]["message"], colour = ctx.author.color)
            await ctx.reply(embed=embed)
          else:
            for item in response["data"]:
              await ctx.send(item["url"])

  @commands.command()
  @commands.has_any_role("SqChatGPT")
  async def codegpt(self, ctx,*, prompt):
    mon = liveness.find_one({"setting":"main"})
    if mon["chatgptsetting"]["live"] == True:
      async with aiohttp.ClientSession() as session:
        payload = {
          "model": "code-davinci-002",
          "prompt": prompt,
          "max_tokens": 500,
          "temperature": mon["chatgptsetting"]["temperature"],
          "presence_penalty": mon["chatgptsetting"]["presence_penalty"],
          "frequency_penalty": mon["chatgptsetting"]["frequency_penalty"],
          "best_of": 1,
          "user": str(ctx.author.display_name)
        }
        headers = {"Authorization": f"Bearer {gptapikey}"}
        async with session.post("https://api.openai.com/v1/completions", json=payload, headers=headers) as res:
          response = await res.json()
          print(response)
          if "error" in response:
            embed = discord.Embed(title="ChatGPT", description=response["error"]["message"], colour = ctx.author.color)
            await ctx.reply(embed=embed)
          else:
            embed = discord.Embed(title="ChatGPT", description=response["choices"][0]["text"], colour = ctx.author.color)
            footer = "Token Usage: " + str(response["usage"]["total_tokens"])
            embed.set_footer(text=footer)
            await ctx.reply(embed=embed)

  @commands.command()
  async def oldgpt(self, ctx,*, prompt):
    mon = liveness.find_one({"setting":"main"})
    if mon["chatgptsetting"]["live"] == True:
      async with aiohttp.ClientSession() as session:
        payload = {
          "model": mon["chatgptsetting"]["model"],
          "prompt": prompt,
          "max_tokens": 2048,
          "temperature": mon["chatgptsetting"]["temperature"],
          "presence_penalty": mon["chatgptsetting"]["presence_penalty"],
          "frequency_penalty": mon["chatgptsetting"]["frequency_penalty"],
          "best_of": 1
        }
        headers = {"Authorization": f"Bearer {gptapikey}"}
        async with session.post("https://api.openai.com/v1/completions", json=payload, headers=headers) as res:
          response = await res.json()
          print(response)
          if "error" in response:
            embed = discord.Embed(title="ChatGPT", description=response["error"]["message"], colour = ctx.author.color)
            await ctx.reply(embed=embed)
          else:
            embed = discord.Embed(title="ChatGPT", description=response["choices"][0]["text"], colour = ctx.author.color)
            footer = "Token Usage: " + str(response["usage"]["total_tokens"])
            embed.set_footer(text=footer)
            await ctx.reply(embed=embed)

  @commands.command()
  @commands.is_owner()
  async def setgpt(self, ctx, para, value):
    if para.lower() in ['max_token']:
      liveness.update_one({"setting":"main"}, {"$set":{f"chatgptsetting.{para}":int(value)}})
      embed = discord.Embed(title="ChatGPT Update", description=f"New {para}: {value}", colour = ctx.author.color)
      await ctx.reply(embed=embed)
    elif para.lower() in ['model','chatmodel','system','imagesize']:
      liveness.update_one({"setting":"main"}, {"$set":{f"chatgptsetting.{para}":str(value)}})
      embed = discord.Embed(title="ChatGPT Update", description=f"New {para}: {value}", colour = ctx.author.color)
      await ctx.reply(embed=embed)
    elif para.lower() in ['temperature','presence_penalty','frequency_penalty']:
      liveness.update_one({"setting":"main"}, {"$set":{f"chatgptsetting.{para}":float(value)}})
      embed = discord.Embed(title="ChatGPT Update", description=f"New {para}: {value}", colour = ctx.author.color)
      await ctx.reply(embed=embed)
    else:
      embed = discord.Embed(title="ChatGPT Wrong Parameters", description=f"> model\n> max_token\n> temperature\n> presence_penalty\n> frequency_penalty", colour = ctx.author.color)
      await ctx.reply(embed=embed)

def setup(client):
  client.add_cog(CHATGPT(client))
