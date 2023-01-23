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
    if mon["chatgpt"] == True:
      async with aiohttp.ClientSession() as session:
        payload = {
          "model": "text-davinci-003",
          "prompt": prompt,
          "max_tokens": 50,
          "temperature": 0.5,
          "presence_penalty": 0,
          "frequency_penalty": 0,
          "best_of": 1
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
