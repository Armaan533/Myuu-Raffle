import discord
from discord.ext import commands
import logical_definitions as lgd
import mongo_declarations as mn

class mytickets(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = "mytickets", aliases = ["Mytickets", "myticket", "Myticket", "mytix", "Mytix", "mt", "Mt", "MT"])
    async def mytickets(self, ctx):
        if str(ctx.guild.id) not in mn.raffledbase.list_collection_names():
            await ctx.reply(embed = discord.Embed(
                title = "No raffle found",
                description = "No raffle has been created for this guild",
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
            ))

        else:
            authorid = ctx.author.id
            guildraffle = mn.raffledbase[str(ctx.guild.id)]
            tickets = guildraffle.find_one({"_id":authorid},{"_id":0,"tickets":1})["tickets"]
            rafflename = guildraffle.find_one({"_id":"Raffle"},{"_id":0,"RaffleName":1})["RaffleName"]
            await ctx.reply(embed = discord.Embed(
                title = "Tickets",
                description = f"You have bought {tickets} ticket(s) for raffle {rafflename}",
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
            ))

def setup(client):
    client.add_cog(mytickets(client))