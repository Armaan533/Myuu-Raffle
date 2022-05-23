from cogs.mytickets import mytickets
from discord.ext import commands
import discord
import logical_definitions as lgd
import mongo_declarations as mn

class total_earning(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_guild_permissions(administrator = True)
    async def total_earning(self, ctx):
        if not str(ctx.guild.id) in mn.raffledbase.list_collection_names():
            noRaffleEmbed = discord.Embed(
			    title = "No Raffles Found", 
			    description = "There are no raffles in this guild going on\nIf you wanna create new raffle then try ``rafflecreate`` command", 
			    color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		    )
            await ctx.reply(embed = noRaffleEmbed)
        else:
            guild = mn.raffledbase[str(ctx.guild.id)]
            total_tickets = 0
            ticketCost = guild.find_one({"_id":"Raffle"},{"_id":0,"Ticket Cost":1})["Ticket Cost"]
            raffleName = guild.find_one({"_id":"Raffle"},{"_id":0,"RaffleName":1})["RaffleName"]
            for i in guild.find({"type":"buyer"},{"_id":0,"tickets":1}):
                total_tickets += i["tickets"]
            
            pkcEarned = total_tickets*ticketCost
            earningEmbed = discord.Embed(
                title = "Total Earnings",
                description = f"Raffle ``{raffleName}`` earned {pkcEarned} pkc",
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
            )
            await ctx.reply(embed = earningEmbed)

def setup(client):
    client.add_cog(total_earning(client))
