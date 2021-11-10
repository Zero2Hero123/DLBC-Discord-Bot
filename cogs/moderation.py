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

no_Permission = discord.Embed(description="Sorry, you don't have permission to run that command.",color=0xde370d)

class Moderation(commands.Cog):

  def __init__(self,client):

    self.client = client

  @commands.command()
  async def mute(self,ctx,member: discord.Member=None,duration=None,*,reason=None):
    audit_log = self.client.get_channel(895826386416193626)

    if member != None:
      if ctx.message.author.top_role.permissions.manage_roles == True:


        await ctx.message.delete(delay=None)
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        units = {
          "m": 60, # 60 seconds = 1 minute
          "h": 3600 # 3600 seconds = 1 hour
        }

        amount = duration[:-1]
        amount = int(amount)
        unit = duration[-1]

        if unit == "m":
          audit_embed = discord.Embed(title=f"🤐 Muted **{member.name}**#{member.discriminator}",description=f"Mute Duration: ``{amount}`` minute(s)",color=0x757171)
        elif unit == "h":
          audit_embed = discord.Embed(title=f"🤐 Muted **{member.name}**#{member.discriminator}",description=f"Mute Duration: ``{amount}`` hour(s)",color=0x757171)
        
        audit_embed.set_thumbnail(url=f"{member.avatar_url}")
        audit_embed.set_author(name=f"Moderator: {ctx.message.author}",icon_url=f"{ctx.message.author.avatar_url}")
        audit_embed.add_field(name="Reason:",value=f"{reason}",inline=False)
        audit_embed.timestamp = dt.datetime.utcnow()

        mute_embed = discord.Embed(title="",description=f"**{member} has been muted temporarily.** | **__Reason:__** {reason}",color=0x7fbef5)
        mute_embed.timestamp = dt.datetime.utcnow()

        roles = member.roles
        roles.remove(roles[0])

        for role in roles:
          await member.remove_roles(role)
        await member.add_roles(muted_role, reason=reason)

        await ctx.send(embed=mute_embed)


        if unit == "m":
          unmute_embed = discord.Embed(title=f"🗣️ Unmuted **{member.name}**#{member.discriminator}",description="Mute Duration: ``0``",color=0x5ef26d)

          unmute_embed.add_field(name="Reason: ",value="Mute Duration Expired",inline=False)
          unmute_embed.set_author(name=f"Moderation Bot: DLBC Usher",icon_url=f"{ctx.guild.icon_url}")
          unmute_embed.set_thumbnail(url=f"{member.avatar_url}")
          unmute_embed.timestamp = dt.datetime.utcnow()

          await audit_log.send(embed=audit_embed)
          await asyncio.sleep(amount * units["m"])
          await member.remove_roles(muted_role)

          for role in roles:
            await member.add_roles(role)
          await audit_log.send(embed=unmute_embed)
        elif unit == "h":
          unmute_embed = discord.Embed(title=f"🗣️ Unmuted **{member.name}**#{member.discriminator}",description="Mute Duration: ``0``",color=0xcecdd4)

          unmute_embed.add_field(name="Reason: ",value="Mute Duration Expired",inline=False)
          unmute_embed.set_author(name=f"Moderation Bot: DLBC Usher",icon_url=f"{ctx.guild.icon_url}")
          unmute_embed.set_thumbnail(url=f"{member.avatar_url}")
          unmute_embed.timestamp = dt.datetime.utcnow()

          await audit_log.send(embed=audit_embed)
          await asyncio.sleep(amount * units["h"])
          await member.remove_roles(muted_role)

          for role in roles:
            await member.add_roles(role)
          await audit_log.send(embed=unmute_embed)

      else:
        response = await ctx.send(embed=no_Permission)
        await response.delete(delay=4)
    else:
      await ctx.send("Please specify a member to mute.")
  
  @commands.command()
  async def unmute(self,ctx,member: discord.Member=None):
    audit_log = self.client.get_channel(895826386416193626)

    if member != None:
      if ctx.message.author.top_role.permissions.manage_roles == True:
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if muted_role in member.roles:

          unmute_embed1 = discord.Embed(title="",description=f"**{member} has been unmuted.**",color=0x7fbef5)

          unmute_embed = discord.Embed(title=f"🗣️ Unmuted **{member.name}**#{member.discriminator}",description="Mute Duration: ``0``",color=0xcecdd4)

          unmute_embed.add_field(name="Reason: ",value="Mute Duration Expired",inline=False)
          unmute_embed.set_author(name=f"Moderation Bot: DLBC Usher",icon_url=f"{ctx.guild.icon_url}")
          unmute_embed.set_thumbnail(url=f"{member.avatar_url}")
          unmute_embed.timestamp = dt.datetime.utcnow()

          await member.remove_roles(muted_role)
          await ctx.send(embed=unmute_embed1)
          await audit_log.send(unmute_embed)
        else:
          await ctx.message.reply("This member isn't muted.")
      else:
        response = await ctx.send(embed=no_Permission)
        await response.delete(delay=4)
    else:
      await ctx.send("Please specify a member to unmute.")



def setup(client):
  client.add_cog(Moderation(client))