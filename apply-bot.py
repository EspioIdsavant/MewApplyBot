# bot.py
import os
import random
import shelve
import asyncio

import discord
from discord.ext import commands

import sys, traceback

intents = discord.Intents(messages=True, guilds=True)

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

def listguilds():
    d = shelve.open("guilds")
    guildlist = d['list']
    listtext = "```"
    for gld in guildlist:
        gldict = d[gld]
        lineout = f"{gldict['display']}    | {gldict['count']}/30    | {gldict['type']}    | {gldict['reqs']}\n"
        listtext = listtext + lineout
    listtext = listtext + "```"
    d.close()
    return listtext

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = ['~', 'wakkawakka']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ? to be used in DMs
        return '?'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)

initial_extensions = ['admin']


bot = commands.Bot(command_prefix=get_prefix, description='Manages private applications for MewMewCorps', intents=intents)

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)



class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None




@bot.command(name='apply', help='Start the application process to MewMewCorps',pass_context=True)
async def start_apply(ctx):

    applicant = ctx.author
    guild = ctx.guild
    appdisp = applicant.display_name
    channel = ctx.channel
    category = channel.category

    if category.name.lower() != 'applications':
        await ctx.send(f"I'm sorry ~~Dave~~ {applicant.mention} I can't let you do that.  The apply command can only be run from the #apply-to-mew channel.", delete_after = 10)
        await ctx.message.delete()
        return;
    
    response = f"Hello, {appdisp} I see your application request"
    await ctx.send(response, delete_after = 5)
    await ctx.message.delete()

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await guild.create_text_channel(f"app-for-{appdisp}", overwrites=overwrites, category=category)
    await channel.set_permissions(applicant, read_messages=True, send_messages=True)
    await channel.send(f"Hello {appdisp}!  This is a private channel just for your application to join MewMewCorps!  Currently only you and the bots can see it.  To get started, first tell us which guild you wish to join!")
    await channel.send("To do this, type **~join**, followed by the name of the guild you want to apply for.")
    gllist = listguilds()
    await channel.send("Our current bot supported guilds:")
    await channel.send(gllist)
    await channel.send("MewCorps guilds not on the list above still use the old fashioned channels.")
    await channel.send("Type **~help** to see all the bot commands available")

    response2 = f"I have created the private channel #{channel} for your application!  Please go there to continue the process.  This message will self destruct in 5 seconds."
    sent2 = await ctx.send(response2, delete_after = 5)

@bot.command(name='join', help='Pick a guild to start applying to',pass_context=True)
async def start_join(ctx, tojoin):

    applicant = ctx.author
    guild = ctx.guild
    appdisp = applicant.display_name
    channel = ctx.channel
    category = channel.category
    

    d = shelve.open('guilds')
    guildlist = d['list']

    #if tojoin.lower() == "mystic":
    #    await ctx.send("Get the fuck out of here.")
    #    await applicant.kick();
    #    return
    
    try: 
        x = guildlist.index(tojoin.lower())
    except:
        x = -1

    if x == -1:
        await ctx.send(f"I'm sorry, the guild {tojoin} does not exist. Please try again")
        return

    guildinfo = d[tojoin]
    await ctx.send(f"Ok so you want to join {tojoin}.  The requirements for this guild are {guildinfo['reqs']}")
    await ctx.send(f"The guild leader is {guildinfo['leader']}.  I've added them to this private channel.  Please provide your requirement evidence as well as any other relevant information for your application.")
    await ctx.send("You can apply to more then one guild at once.  Type additional ~join commands to have guild leaders fight over you.")
    
@bot.command(name='withdraw', help='Withdraw your application to MewMewCorps',pass_context=True)
async def stop_apply(ctx):

    applicant = ctx.author
    guild = ctx.guild
    appdisp = applicant.display_name
    appdisp = appdisp.lower()
    appdisp = appdisp.replace(" ", "-")
    channel = ctx.channel
    category = channel.category
    leaders = discord.utils.get(guild.roles,name="Guild Leader")

    expectedname = f"app-for-{appdisp}"

    if channel.name != expectedname:
        await ctx.send(f"You can only withdraw your application from your private application channel ({expectedname}).", delete_after = 10)
        await ctx.message.delete()
        return;

    await ctx.send("Application withdrawl acknowledged.  Feel free to apply again later.  Goodbye.")
    await asyncio.sleep(60)
    await channel.set_permissions(applicant, read_messages=False,send_messages=False)
    await channel.set_permissions(leaders, read_messages=True,send_messages=True)
    await ctx.send(f"Attn {leaders.mention}: {appdisp} has withdrawn thier application.  Use *~closeapp* to remove this channel after you are done with it.")

@bot.command(name='closeapp', help='Close application channel',pass_context=True)
@commands.has_any_role("Guild Leader")
async def kill_channel(ctx):

    guild = ctx.guild
    channel = ctx.channel
    category = channel.category


    if not channel.name.startswith("app-for-") :
        await ctx.send(f"You can only close application channels", delete_after = 10)
        await ctx.message.delete()
        return;

    await ctx.send("Channel closing")
    await channel.delete()


bot.run(TOKEN)
bot.add_cog(Admin(bot))

