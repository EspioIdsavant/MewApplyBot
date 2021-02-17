import discord
from discord.ext import commands


class AdminCog(commands.Cog, name="Administration"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='addguild', help='Admin only: Add a new MewCorps guild',pass_context=True,category='Admin')
    async def addguild(ctx, name, display, leader, count, gtype, reqs):
        d = shelve.open('guilds')
        guildlist = d['list']
        name = name.lower()
        

        try: 
            x = guildlist.index(name)
        except:
            x = -1

        if x >= 0:
            await ctx.send(f"Guild name {name} already exists", delete_after = 5)
            return
        
        newdict = {
            "name": name,
            "display": display,
            "leader": leader,
            "count": count,
            "type": gtype,
            "reqs": reqs
        }

        guildlist.append(name)
        d['list'] = guildlist
        d[name] = newdict
        d.close()

    @commands.command(name='updateguild', help='Admin only: Update a MewCorps guild',pass_context=True)
    async def updateguild(ctx, name, leader, count, gtype, reqs):
        d = shelve.open('guilds')
        guildlist = d['list']
        

        try: 
            x = guildlist.index(name)
        except:
            x = -1

        if x == -1:
            await ctx.send(f"Guild name {name} does not exist", delete_after = 5)
            return
        
        newdict = {
            "name": name,
            "leader": leader,
            "count": count,
            "type": gtype,
            "reqs": reqs
        }

        d[name] = newdict
        d.close()


    @commands.command(name='init', help='Admin only: Initalize the bot',pass_context=True)
    @commands.has_any_role("apply_admin")
    async def start_bot(ctx):
        owner = ctx.author
        guild = ctx.guild
        channel = ctx.channel
        passed = 0
        failed = 0
        
        await channel.purge()

        await channel.send("Welcome to the MewMewCorps application channel!  To apply to any of our guilds, type **~apply** to start the process.")
        gllist = listguilds()
        await channel.send("Our current guilds:")
        await channel.send(gllist)
        await channel.send("MewCorps guilds not on the list above still use the old fashioned channels.")
        await channel.send("Type **~help** to see all the bot commands available")

def setup(bot):
    bot.add_cog(AdminCog(bot))
