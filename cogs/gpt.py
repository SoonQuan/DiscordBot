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
          "best_of": 1,
          "user": str(ctx.author.display_name)
        }
        headers = {"Authorization": f"Bearer {gptapikey}"}
        async with session.post("https://api.openai.com/v1/completions", json=payload, headers=headers) as res:
          response = await res.json()
          embed = discord.Embed(title="ChatGPT", description=response["choices"][0]["text"])
          footer = "Token Usage: " + str(response["usage"]["total_tokens"])
          embed.set_footer(text=footer)
          await ctx.reply(embed=embed)

def setup(client):
  client.add_cog(CHATGPT(client))
