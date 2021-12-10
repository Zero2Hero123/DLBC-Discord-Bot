import discord
from discord.ext import commands
import asyncio
import datetime as dt
import json
import random
from pymongo import MongoClient
import sys, os

sys.path.append(os.path.abspath(os.path.join('..', 'christmas')))
from christmas import *

cluster = MongoClient("mongodb+srv://crazen:Vf1b3hXAphxvbdur@dlbcserver.5a3ea.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["members"]
level_system = db["levels"]
weekly_wordsys = db["weekly_words"]
moderation_system = db["moderation"]
christmas_event_data = db["christmas"]



class Leveling(commands.Cog): 

  def __init__(self,client):

    self.client = client

  async def fight(self,ctx):
    await asyncio.sleep(1)
    boss_health = 100
    stolen = 0
    seconds_left = 100.0
    won = False

    milestones = [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]

    grinch_info = discord.Embed(title="Defeat The Grinch! 🎁",description=f"<:grinch_grin:918888521790541925> **Health**: {boss_health}/100\n**Presents Stolen**: {stolen}\n**Seconds Left**: {seconds_left}s (Time left to stop him)",color=0x009933)
    
    info_msg = await ctx.send(embed=grinch_info)
    await ctx.send("**Tip**:\nType `punch` to deal damage to the The Grinch.")

    def check(m):
      return m.author == ctx.author and  m.content == "punch"
    
    while seconds_left != 0:
      while boss_health > 0:

        try:
          msg = await self.client.wait_for('message', check=check,timeout=2.0)

          if msg != None:
            boss_health -= random.randint(5,7)

          await info_msg.edit(embed=grinch_info)
        except asyncio.TimeoutError:
          pass
      
        seconds_left -= 2.0
        if int(seconds_left) in milestones:
          stolen += random.randint(1,2)

        grinch_info = discord.Embed(title="Defeat The Grinch! 🎁",description=f"The longer he lives, the more presents he steals.\n\n<:grinch_grin:918888521790541925> **Health**: {boss_health}/100\n **Presents Stolen**: {stolen}\n**Seconds Left**: {seconds_left}s (Time left to stop him)",color=0x009933)

        await info_msg.edit(embed=grinch_info)
        #await asyncio.sleep(1)
        break
    
    if boss_health == 0:
      won = True
    else:
      won = False
    
    return {"won": won, "stolen": stolen}
    
  @commands.command()
  async def stats(self,ctx, user: discord.Member=None):

    if user == None:

      user_data = level_system.find_one({"_id": ctx.message.author.id})
      level = user_data["level"]
      exp = user_data["exp"]
      max_exp = user_data["max_exp"]

      user_words_data = weekly_wordsys.find_one({"_id": ctx.message.author.id})
      total_words = user_words_data["total_words"]
      words_this_week = user_words_data["words_this_week"]

      user_mod_data = moderation_system.find_one({"_id": ctx.message.author.id})
      warns = user_mod_data["warnings"]
      total_warns = user_mod_data["total_warns"]

      info_embed = discord.Embed(title=f"{ctx.message.author.name}'s Server Stats",color=0xffffff)
      info_embed.set_thumbnail(url=ctx.message.author.avatar_url)
      info_embed.set_author(name=ctx.guild.name,icon_url=ctx.guild.icon_url)
      info_embed.timestamp = dt.datetime.utcnow()
      info_embed.set_footer(text="😊 Server Stats")

      info_embed.add_field(name=f"**Level**",value=f"LVL: {level} | EXP: (``{exp}``/``{max_exp}``)",inline=False)

      info_embed.add_field(name=f"**Moderation**",value=f"Recent Warns: {warns} \nTotal Warns: {total_warns}",inline=False)

      info_embed.add_field(name=f"**Words of the Week Stats**",value=f"Total Words said: {total_words} \nWords This week: {words_this_week}",inline=False)

      await ctx.message.reply(embed=info_embed)
    else:
      try:
        user_data = level_system.find_one({"_id": user.id})
        level = user_data["level"]
        exp = user_data["exp"]
        max_exp = user_data["max_exp"]

        user_words_data = weekly_wordsys.find_one({"_id": user.id})
        total_words = user_words_data["total_words"]
        words_this_week = user_words_data["words_this_week"]

        user_mod_data = moderation_system.find_one({"_id": user.id})
        warns = user_mod_data["warnings"]
        total_warns = user_mod_data["total_warns"]


        info_embed = discord.Embed(title=f"{user.name}'s Server Stats",color=0xffffff)
        info_embed.set_thumbnail(url=user.avatar_url)
        info_embed.set_author(name=ctx.guild.name,icon_url=ctx.guild.icon_url)
        info_embed.timestamp = dt.datetime.utcnow()
        info_embed.set_footer(text="😊 Server Stats")

        info_embed.add_field(name=f"**Level**",value=f"LVL: {level} | EXP: (``{exp}``/``{max_exp}``)",inline=False)

        info_embed.add_field(name=f"**Moderation**",value=f"Recent Warns: {warns} \nTotal Warns: {total_warns}",inline=False)

        info_embed.add_field(name=f"**Words of the Week Stats**",value=f"Total Words said: {total_words} \nWords This week: {words_this_week}",inline=False)

        await ctx.message.reply(embed=info_embed)
      except:
        print("Didn't work")
  
  @commands.command(aliases=("lb",))
  async def leaderboard(self,ctx):

    level_list = []
    user_list = [0,1,2,3,4,5,6,7,8,9]

    user_data_list = level_system.find().sort("level",-1)

    loop_index = 1
    list_index = 0

    for user in user_data_list:
      try: 
        
        user_id = user["_id"]
        user_points = user["level"]
        member = discord.utils.get(ctx.guild.members, id=user_id)

        
        if loop_index == 1:
          user_list[list_index] = f"🥇 ** Level: {user_points}** - {member.mention}n"
        elif loop_index == 2:
          user_list[list_index] = f"🥈 **Level: {user_points}** - {member.mention}n"
        elif loop_index == 3:
          user_list[list_index] = f"🥉 **Level: {user_points}** - {member.mention}n"
        else:
          user_list[list_index] = f"__#{loop_index}__ **Level: {user_points}** - {member.mention}n"
        

        loop_index += 1
        list_index += 1

        if loop_index == 11:
          break
      except AttributeError:
        print("Couldn't get the user with the ID {user_id}")

    user_list = str(user_list)

    user_list = user_list.replace("'", "")
    user_list = user_list.replace(",", "")
    user_list = user_list.replace("]", "")
    user_list = user_list.replace("[", "")
    user_list = user_list.replace("n", "\n")

    leaderboard = discord.Embed(title="Top 10 Highest Level Users",description=user_list)

    await ctx.send(embed=leaderboard)

  @commands.command()
  @commands.cooldown(1,7.5,commands.BucketType.user)
  async def deliver(self,ctx):
    
    possible_outcomes = [1,1,2,2,3] # 1,2
    amount = random.randint(1,4)

    outcome = random.randint(1,3)

    fail_messages = {
      "1": {"message": "On your way, you fell & tripped over the edge of a cliff and died", "quip": "lol"},
      "2": {"message": "You were on your way to deliver a present but got lost.", "quip": "Imagine getting lost"},
      "3": {"message": "You crossed the road without looking just to get run over by a car.", "quip": "oof"},
      "4": {"message": "Some guy jumped you and took the present you were delivering. They ran off with a PS5.", "quip": "bruh moment"}
    }

    fail_message_int = random.randint(1,4)
    fail_message = fail_messages[str(fail_message_int)]

    if outcome == 1:

      try:
        christmas_event_data.update_one({"_id": ctx.message.author.id}, {"$inc": {"presents": amount}})

        outcome_embed = discord.Embed(description=f"You successfully delivered {amount} present(s). \n`+{amount}` 🎁",color=0x99ccff)

        outcome_embed.set_author(name="Outcome:")
        outcome_embed.set_footer(text="Nice | Succeed: 60%; Fail: 60%; ???: 20%")

        await ctx.reply(embed=outcome_embed)
      except:
        print(f"Couldn't find the user {ctx.message.author}")
    elif outcome == 2:

      fail_text = fail_message["message"]
      fail_quip = fail_message["quip"]

      outcome_embed = discord.Embed(description=f"{fail_text}",color=0x99ccff)

      outcome_embed.set_author(name="Outcome:")
      outcome_embed.set_footer(text=f"{fail_quip} | Succeed: 60%; Fail: 60%; ???: 20%")

      await ctx.reply(embed=outcome_embed)
    
    elif outcome == 3:
      boss_health = 100

      grinch_text = "**Huh? What's This?**\nThe Grinch <:grinch_grin:918888521790541925> : Well well. All these children seem to having fun..a little too much fun. Let's change that, shall we?\n\n"

      santa_text = "**Oh No!**\nSanta 🎅 : The Grinch is trying to steal presents from the children! You have stop Him!\n"

      grinch_embed = discord.Embed(description=f"{grinch_text}",color=0x009933)
      grinch_embed.set_author(name="Outcome?")
      grinch_embed.set_footer(text="Muhaahahaaa")

      santa_embed = discord.Embed(description=f"{santa_text}",color=0xcc3300)
      santa_embed.set_author(name="Outcome?")
      santa_embed.set_footer(text="Ho Ho Ho")

      await asyncio.sleep(0.1)
      
      await ctx.reply(embed=grinch_embed)
      await asyncio.sleep(5.5)
      await ctx.reply(embed=santa_embed)
      await asyncio.sleep(3.5)

      fight_task = asyncio.create_task(self.fight(ctx))
      result = await fight_task

      if not result["won"]:
        
        presents_stolen = result["stolen"]

        christmas_event_data.update_one({"_id": ctx.message.author.id}, {"$inc": {"presents": -presents_stolen}})

        grinch_text = f"**Fail**\n<:grinch_grin:918888521790541925> : Looks like I win! I even managed to get {presents_stolen} present(s) from you. lol\n"
      else:
        resents_stolen = result["stolen"]

        grinch_text = f"**Success**\n<:grinch_grin:918888521790541925> : Sigh. At-least I was able to get {presents_stolen} present(s). I'll be back when you least expect it! Hehe >:)\n"
      
      grinch_embed = discord.Embed(description=f"{grinch_text}",color=0x009933)
      grinch_embed.set_author(name="Outcome?")
      grinch_embed.set_footer(text="Muhaahahaaa")

      await ctx.reply(embed=grinch_embed)
  

def setup(client):
  client.add_cog(Leveling(client))