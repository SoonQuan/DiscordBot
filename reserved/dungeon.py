import discord
import os
from discord.ext import commands, tasks
from itertools import cycle

client = commands.Bot(command_prefix=">", description="Bot is here for your entertainment",case_insensitive=True)
botcolour = 0x0fa4aab
status = cycle(["with your luck", "with you | try !help"])


@client.event
async def on_ready():
  change_status.start()
  print('We have logged in as {0.user}'.format(client))

@tasks.loop(minutes=11)
async def change_status():
  await client.change_presence(activity=discord.Game(next(status)))

"""
RPG dungeon
|
----- Character
      |
      ----- Stamina
            |
            ----- Combat : Monster/Dungeon = 5 
                  |
                  ---- Regen 1 every 1 hour
            |
            ----- AP/Action Point : Travel = 19 + (Level)
                  |
                  ---- Regen 1 every 5 minutes
      |
      ----- Levels: 1 
            |
            ----- Experience
                  |
                  ----- Required per level = 50 * (1+(Level-1)**2)
      |
      ----- Stat
            |
            ----- Strength
                  |
                  ----- Base Stat: 5
                  |
                  ----- Equipment Bonus
            |
            ----- Defence
                  |
                  ----- Base Stat: 5
                  |
                  ----- Equipment Bonus
            |
            ----- Dexterity
                  |
                  ----- Base Stat: 5
                  |
                  ----- Equipment Bonus
            |
            ----- HP base = 5*(Levels-1)+50
            |
            ----- Hidden Stat
                  |
                  ----- Luck
                  |
                  ----- Bloodlust
      |
      ----- Equipment
            |
            ----- Name
            |
            ----- Required level
            |
            ----- Rating 
            |
            ----- Durability 
            |
            ----- Stat bonus
            |
            ----- NPC/NPC worth
      |
      ----- Combat
            |
            ----- Attack
                  |
                  ----- Max = User(str) - (9/11)*Target(def)
                  |
                  ----- Min = User(str) - (11/9)*Target(def)
                  |
                  ----- Hitrate = (7/2)*(User(dex)/Target(def)) # range of 0 to 1
            |
            ----- Item
                  |
                  ----- Use item
                  |
                  ----- Added bonus
      |
      ----- PVP
            |
            ----- Combat
            |
            ----- Conditions
                  |
                  ----- More than half HP
                  |
                  ----- Must be level 5 or higher
            |
            ----- Benefits
                  |
                  ----- Winning
                        |
                        ----- 33% to win 5% of Target inv
                        ----- 20% to win 9% of Target inv
                        ----- 10% to win 12% of Target inv
                        ----- 37% to win nothing
                  |
                  ----- Losing
                        |
                        ----- Lose HP
|
----- Monster
      |
      ----- Levels
      |
      ----- Stat
      |
      ----- Drops
|
----- Merchant
      |
      ----- Levels/Ranks?
      |
      ----- Items/Equipment
      |
      ----- Sales for drops
|
----- Dungeon
      |
      ----- Levels/Depth & Tier
      |
      ----- Monsters
      |
      ----- Treasure
|
----- Travel
      |
      ----- Step Cost: 4 AP 
      |
      ----- Events
            |
            ----- 1. Basic: 1-5000 currency or 1-level experience
            |
            ----- 2. Item drop: any rating and required level of +-3 User level
            |
            ----- 3. Encounter: random User clone's --Combat
            |
            ----- 4. Nothing lol



"""





client.run(os.getenv('TOKEN'))