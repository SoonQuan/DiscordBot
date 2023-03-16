import os, discord, aiohttp
from discord.ext import commands
import pymongo
from pymongo import MongoClient

cluster = MongoClient(os.getenv('MONGODB'))
gptapikey = os.getenv('GPTAPIKEY')
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

class CHATGPT(commands.Cog):
  """ GPT commands """
  def __init__(self,client):
    self.client = client

  @commands.command()
  @commands.has_any_role("SqChatGPT")
  async def gpt(self, ctx,*, prompt):
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
  async def image(self, ctx,*, prompt):
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
    elif para.lower() in ['model']:
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
