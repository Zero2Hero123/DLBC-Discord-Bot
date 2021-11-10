import os
import discord
import asyncio
intents = discord.Intents.default()
intents.members = True
from discord.ext import commands, tasks
from webserver import keep_alive
from discord.ext.commands import Bot
from discord_components import *
import random
import json
import datetime as dt
import time
import pymongo
from pymongo import MongoClient
from utils import *

cluster = MongoClient("mongodb+srv://crazen:Vf1b3hXAphxvbdur@dlbcserver.5a3ea.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["members"]
level_system = db["levels"]
moderation_system = db["moderation"]
weekly_wordsys = db["weekly_words"]
weekly_word_loop_data = db["weekly_word_data"]

client = ComponentsBot(command_prefix = '.',intents=intents)

# bot = ComponentsBot(command_prefix = ".")
cogs = ["cogs.leveling","cogs.moderation"]

for cog in cogs:

  client.load_extension(cog)
  print(f"Loaded cog {cog}")

# assests
no_Permission = discord.Embed(description="Sorry, you don't have permission to run that command.",color=0xde370d)

bad_words = ["test123","hentai","Hentai","porn","cunt","idgaf","wtf","WTF","niga","nigger","nigga","vagina","puss","pussy","dick","d1ck","d!ck","bich","bitch","bitc","Bitch","BITCH","BICH","fack","fak","fuck","fuk","Fuck","Fuk","CUNT","Cunt","asshole","🖕","shit","sh!t","sh1t","shii","a$$","shi","shii","shiii","shiiii","faggot","fag","Faggot","Fag","mfs","mf","stfu","Stfu","STFU"]

# WEEKLY WORDS
weekly_words = {
  "1": ["thanks","great","amen","nice","cool"],
  "2": ["brethren","amazing","gg","morning"]
}

# TASKS LOOPS
@tasks.loop(minutes=1)
async def weekly_words_loop():
  weekly_word_channel = client.get_channel(896880737318498375)

  today = dt.date.today()

  if today.strftime("%a") == "Sun":

    weekly_data = weekly_word_loop_data.find_one({"_id": 1})

    day = weekly_data["last_sent"]["day"]
    month = weekly_data["last_sent"]["month"]
    year = weekly_data["last_sent"]["year"]

    check_date = dt.date(year,month,day)

    if today != check_date:
      # RESET current words
      last_list = weekly_data["current_list"]
      list_number = random.randint(1,2)

      while list_number == last_list:
        list_number = random.randint(1,2)
        print(f"New List: {list_number}")

      new_year = today.year
      new_month = today.month
      new_day = today.day

      x = {"current_count": list_number}

      weekly_word_loop_data.update_one({"_id": 1}, {"$set": x})

      new_dates = {"year": new_year,"month": new_month, "day": new_day}

      weekly_word_loop_data.update_one({"_id": 1}, {"$set": {"last_sent": new_dates}})

      print("words reset")

      
      list_of_words = weekly_words[f"{list_number}"]
      list_of_words = list(list_of_words)
      list_of_words = str(list_of_words)

      list_of_words = list_of_words.replace("'", "")
      list_of_words = list_of_words.replace(",", ",")
      list_of_words = list_of_words.replace("]", "'")
      list_of_words = list_of_words.replace("[", "'")

      weekly_embed = discord.Embed(title="New Week, New Words!",description=f"This week's Weekly words are {list_of_words}",color=0x66ff66)
      weekly_embed.timestamp = dt.datetime.utcnow()
      weekly_embed.set_footer(text="Weekly words Reset every Week.")

      for user_data in weekly_wordsys.find():
        
        user_id = user_data["_id"]

        weekly_wordsys.update_one({"_id": user_id}, {"$set": {"words_this_week": 0}})

        print(f"Reset Word_this_week for User {user_id}.")


      await weekly_word_channel.send(embed=weekly_embed)


# Each Suday, send the YT livestream link in the server; WIP
@tasks.loop(minutes=1)
async def youtube():

  today_date = dt.date.today()

  if today.strftime("%a") == "Mon" or today.strftime("%a") == "Sun":

    try:
      pass

    except:
      pass


# EVENTS
@client.event
async def on_ready():
  DiscordComponents(client)
  print('We have logged in as {0.user}'
  .format(client))

  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name="DLBC Baltimore YT"))

  weekly_words_loop.start()

@client.event
async def on_message(message):
  usher_log = client.get_channel(895826386416193626)
  author = message.author
  bad_word = False
  muted_role = discord.utils.get(message.guild.roles, name="Muted")

  # If the user is not a bot, then check if their message had a bad word in it.
  if not message.author.bot:

    user_mod_data = moderation_system.find_one({"_id": message.author.id})
    if user_mod_data == None: # If the person isnt in the database
      if not message.author.bot:
        post = {"_id": message.author.id, "warnings": 0,"total_warns": 0, "mutes": 0,"total_mutes": 0, "is_muted": False}
        moderation_system.insert_one(post)

        print(f"Added {message.author} to Moderation System.")
    
    # Spam Filte

    # Check for any bad words in their message
    for word in bad_words:

      if word in message.content: 
        bad_word = True
        

        if bad_word:
          moderation_system.update_one({"_id": message.author.id}, {"$inc": {"warnings": 1}})
          moderation_system.update_one({"_id": message.author.id}, {"$inc": {"total_warns": 1}})

          user_mod_data = moderation_system.find_one({"_id": message.author.id})
          warns = user_mod_data["warnings"]
          triggered_content = message.content
          await message.delete(delay=None)

          triggered_word = word
          response = await message.channel.send(f"{message.author.mention} 🚫 Profanity is not allowed. This is your **#{warns}** warning.")

          bad_word_embed = discord.Embed(title="🚫 Bad Word Triggered",description=f"Bad Word: `{triggered_word}` was triggered by **{author}**({author.mention})").set_thumbnail(url=author.avatar_url)
          
          bad_word_embed.add_field(name="Message Content:",value=f"```{triggered_content}```",inline=False)

          bad_word_embed.timestamp = dt.datetime.utcnow()
          bad_word_embed.set_footer(text="AUTOMOD")

          await usher_log.send(embed=bad_word_embed)

          await response.delete(delay=5)

          max_warns = 3


          # Check if their they have more than 3 warns.

          user_mod_data = moderation_system.find_one({"_id": message.author.id})
          user_warns = user_mod_data["warnings"]

          if user_warns > max_warns:
            moderation_system.update_one({"_id": message.author.id}, {"$set": {"warnings": 0}})
            moderation_system.update_one({"_id": message.author.id}, {"$inc": {"mutes": 1}})
            moderation_system.update_one({"_id": message.author.id}, {"$inc": {"total_mutes": 1}})
            
            try:
              await message.author.add_roles(muted_role, reason="Attained 4 warns.")
              await message.author.send("You've been muted for attaining 4 warnings. The Duration of your mute sentence is __15 Minutes__")
              moderation_system.update_one({"_id": message.author.id}, {"$set": {"is_muted": True}})
              
              await asyncio.sleep(900)

              await member.remove_roles(muted_role)
              moderation_system.update_one({"_id": message.author.id}, {"$set": {"is_muted": False}})
              m = await message.author.send("You've been unmuted. Make sure to follow the rules next time.")
              await m.add_reaction("👍")
            except:
              print("Couldn't mute that user.")

          
    # WORD OF THE WEEK SYSTEM


    # If the user had no bad word in their message, reward them with 1 exp.
    
    if not bad_word:
      user_data = level_system.find_one({"_id": message.author.id})
      if user_data == None:
        if not message.author.bot:
          post = {"_id": message.author.id, "level": 1, "exp": 0, "max_exp": 100}
          level_system.insert_one(post)

          print(f"Added {message.author} to Level System.")

      leveled_up = add_exp(message.author.id, 1)

      user_level = user_data["level"]
      
      # WEEKLY WORDS SYSTEM
      user_words_data = weekly_wordsys.find_one({"_id": message.author.id})
      if user_words_data == None:
        post = {"_id": message.author.id, "total_words": 0, "words_this_week": 0}
        weekly_wordsys.insert_one(post)

        print(f"Added {message.author} to weekly Words System.")
      # ==================

      if leveled_up:

        await message.author.send(f"Congrats {message.author.mention}! You're now level {user_level}.")


      current_list = weekly_word_loop_data.find_one({"_id": 1})
      list_number = current_list["current_list"]

      is_weekly_word = False

      for word in weekly_words[f"{list_number}"]:

        if word in message.content or word.upper() in message.content or word.lower() in message.content or word.capitalize() in message.content:
          is_weekly_word = True
          break
      
      if len(message.content) < 10:
        is_weekly_word = False
      
      if is_weekly_word:

        user_data = level_system.find_one({"_id": message.author.id})

        x = add_exp(message.author.id, 15)

        weekly_wordsys.find_one({"_id": message.author.id})

        weekly_wordsys.update_one({"_id": message.author.id}, {"$inc": {"total_words": 1}})

        weekly_wordsys.update_one({"_id": message.author.id}, {"$inc": {"words_this_week": 1}})

        if x:
          await message.author.send(f"Congrats you're now level {user_level}.")

  await client.process_commands(message)

@client.event
async def on_member_join(member):

  # Welcome the member
  welcome_embed = discord.Embed(title="New Member Joined!",description="",color=0xf7f7f7)
  welcome_embed.timestamp = dt.datetime.utcnow()
  welcome_channel = client.get_channel(895825031630848060)

  welcome_embed.set_thumbnail(url=member.avatar_url)

  welcome_embed.add_field(name=f"Welcome, {member.mention}!",value="We hope you enjoy your stay :D",inline=False)

  await welcome_channel.send(embed=welcome_embed)

  # If member was muted before then..
  muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

  try:
    user_data = moderation.find_one({"_id": member.id})

    if user_data["is_muted"]:

      uh_oh = discord.Embed(title="Uh Oh!",description="Seems you were muted before you had previously left the server. This is known as evading your punishment so you'll be muted for 10 minutes as a Penalty for leaving when you were previously muted before leaving.",color=0x0099ff)

      await member.send(embed=uh_oh)

      await member.add_roles(muted_role)
      await asyncio.sleep(600)
      await member.remove_roles(muted_role)

      await member.send("Your Mute Penalty has expired.")

      await moderation_system.update_one({"_id": member.id}, {"$set": {"is_muted": False}})
    
  except:
    print("User not in Moderation System.")



@client.event
async def on_command_error(ctx,error):

  if isinstance(error, commands.CommandOnCooldown):

    cooldown = error.retry_after / 60

    cooldown = round(cooldown, 2)

    response = await ctx.reply(content=f"This command is on cooldown. Try again in **{int(cooldown)}** minutes(s).")

    await response.delete(delay=5)
  elif isinstance(error, commands.BadArgument):
    if ctx.message.content.startswith(".setbirthday"):
      await ctx.message.reply("You need to provide a proper day & month. e.g. `.setbirthday 10 29`\n In that exmaple, it's setting the birthday to October 29th.")
  else:
    raise error

@client.event
async def on_button_click(interaction):
  msg = None
  has_roles = {"orchestra": 2,"praise": 2}

  orchestra_role = discord.utils.get(interaction.guild.roles, name="Orchestra Member")
  praise_role = discord.utils.get(interaction.guild.roles, id=895820533181055026)

  if orchestra_role in interaction.user.roles:
      has_roles["orchestra"] = 1
    
  if praise_role in interaction.user.roles:
      has_roles["praise"] = 1

  orchestra_style = has_roles["orchestra"]
  praise_style = has_roles["praise"]

  if interaction.custom_id == "choose_roles":

    msg = await interaction.send("You click may choose the following roles. To remove the role, just click that button again.",
    components = [
      Button(label="Moderator",emoji="🔨",style=2,custom_id="moderator",disabled=True),
      Button(label="Orchesrta Member",emoji="🎻",custom_id="orchestra_button",style=orchestra_style),
      Button(label="Praise & Worship",emoji="🎤",custom_id="praise_button",style=praise_style)
    ]
    )
  
  if interaction.custom_id == "orchestra_button":
    if interaction.component.style == 1:
      
      await interaction.user.remove_roles(orchestra_role)

      has_roles["orchestra"] = 2

      await interaction.send("Removed Orchestra Role. You may dismiss the message above.")
    elif interaction.component.style == 2:
      await interaction.user.add_roles(orchestra_role)

      await interaction.send("Added Orchestra Role. You may dismiss the message above.")
  elif interaction.custom_id == "praise_button":
    if interaction.component.style == 1:
      
      await interaction.user.remove_roles(praise_role)

      has_roles["praise"] = 2

      await interaction.send("Removed Praise & Worship Role. You may dismiss the message above.")
    elif interaction.component.style == 2:
      await interaction.user.add_roles(praise_role)

      await interaction.send("Added Praise & Worship Role. You may dismiss the message above.")

@client.event
async def on_message_delete(message):
  usher_log = client.get_channel(895826386416193626)

  deleted_embed = discord.Embed(title="Message Deleted",description=f"Message from {message.author.mention} deleted in {message.channel.mention}\n")

  deleted_embed.set_author(name=f"{message.author}",icon_url=f"{message.author.avatar_url}")
  deleted_embed.add_field(name="Message Content:",value=f"```{message.content}```")

  deleted_embed.timestamp = dt.datetime.utcnow()


  await usher_log.send(embed=deleted_embed)


# COMMANDS
@client.command() # CLEAN COMMAND
async def clean(ctx,amount: int=None):
  if amount != None:
    if ctx.message.author.top_role.permissions.manage_messages == True or ctx.channel.id == 789135787492769852:
      
      await ctx.message.delete(delay=None)
      await ctx.channel.purge(limit=amount)
      response2 = await ctx.send(f"{amount} message(s) deleted.")
      await response2.delete(delay=2)
    else:
      response = await ctx.send(embed=no_Permission)
      await response.delete(delay=4)
  else:
    await ctx.send(f"{ctx.message.author.mention} Please specify the number of messages to delete.")

@client.command(aliases=("sm",)) # SLOWMODE Command
async def slowmode(ctx,seconds: int=None):
  slowmode_embed = discord.Embed(title=' ',description=f'Slowmode has been set to ``{seconds}`` second(s).',color=0x7fbef5)

  if seconds != None:

    if ctx.message.author.top_role.permissions.manage_messages == True:
      
      await ctx.message.delete(delay=None)
      await ctx.channel.edit(slowmode_delay=seconds)
      response = await ctx.send(embed=slowmode_embed)

      await response.delete(delay=7)
    else:
      response = await ctx.send(embed=no_Permission)
      await response.delete(delay=4)
  else:
    response = await ctx.send(f"{ctx.message.author.mention} Please specify the number of seconds.")
    await response.delete(delay=3)

@client.command()
@commands.cooldown(1,60,commands.BucketType.guild)
async def votemute(ctx,member: discord.Member=None):

  # VARIABLES
  muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
  total_votes = 0
  voted_users = []
  people_who_voted = []
  usher_log = client.get_channel(895826386416193626)

  if member != None:

    vote_embed = discord.Embed(title="Vote Mute Session",description=f"Should **{member.name}** be muted for 10 minutes?",color=0x7289DA)

    vote_embed.set_thumbnail(url=f"{member.avatar_url}")
    vote_embed.set_author(name=f"{ctx.message.author}",icon_url=f"{ctx.message.author.avatar_url}")
    vote_embed.add_field(name="**Total Votes**:",value=f"`{total_votes}/3`")
    vote_embed.set_footer(text=f"A Minimum of 3 votes is required.")
    vote_embed.add_field(name="**People Who Voted**:",value="None",inline=False)


    vote_msg = await ctx.send(
      embed=vote_embed,
      components = [
        Button(label="Vote",style=1)
      ]
    )

    while total_votes < 3:
      interaction = await client.wait_for("button_click", check = lambda i: i.component.label.startswith("Vote"))

      if interaction.user not in voted_users:
        await interaction.respond(content = "Vote Submitted.")

        if len(voted_users) > 0:
          people_who_voted = people_who_voted.split("\n")
        people_who_voted.append(f"✅ {interaction.user}n")

        people_who_voted = str(people_who_voted)
        people_who_voted = people_who_voted.replace("'", "")
        people_who_voted = people_who_voted.replace(",", "")
        people_who_voted = people_who_voted.replace("]", "")
        people_who_voted = people_who_voted.replace("[", "")
        people_who_voted = people_who_voted.replace("n", "\n")

        voted_users.append(interaction.user)
        total_votes = total_votes + 1

        vote_embed.clear_fields()
        vote_embed.add_field(name="**Total Votes**:",value=f"`{total_votes}/3`")
        vote_embed.add_field(name="**People Who Voted**:",value=f"{people_who_voted}")
        await vote_msg.edit(embed=vote_embed)
      else:
        await interaction.respond(content = "You've already voted.")
    
    await vote_msg.edit(components=[Button(label="Vote Ended",style=1,disabled=True)])
    await asyncio.sleep(1)
    await vote_msg.edit(embed=discord.Embed(title="Vote Ended",description=f"`{member}` has been muted for 10 Minutes | **Total Votes**: {total_votes}/3",color=0x7289DA).set_thumbnail(url=f"{member.avatar_url}"))

    await ctx.message.delete(delay=0)
    await vote_msg.delete(delay=10)

    # Muting the Member
    roles = member.roles
    roles.pop(0)

    if len(roles) > 0:
      for role in roles:

        await member.remove_roles(role)
    
    await member.add_roles(muted_role)

    await member.send("You have been muted for 10 Minutes due Vote Mute")
    await usher_log.send(f"Muted {member.mention} for __10 minutes__ due to Vote mute.")

    # Waiting 10 minutes
    await asyncio.sleep(600)

    # Unmuting the Member
    await member.remove_roles(muted_role)

    for role in roles:
      await member.add_roles(role)

    await member.send("You have been unmuted. Reason: Mute Duration Expired.")

  else:
    msg = await ctx.message.reply(content='Uh, you gotta specify a "Member" to vote-mute buddy.')
    await msg.delete(delay=5)

keep_alive()
client.run(os.environ['TOKEN'])