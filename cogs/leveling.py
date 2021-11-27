import discord
from discord.ext import commands
import asyncio
import datetime as dt
import json
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://crazen:Vf1b3hXAphxvbdur@dlbcserver.5a3ea.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["members"]
level_system = db["levels"]
weekly_wordsys = db["weekly_words"]
moderation_system = db["moderation"]

class Leveling(commands.Cog):

  def __init__(self,client):

    self.client = client
    
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




def setup(client):
  client.add_cog(Leveling(client))