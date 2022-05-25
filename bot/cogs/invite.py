import logical_definitions as lgd
import mongo_declarations as mn
import discord
from discord.ext import commands

class invite(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(name = "invite", aliases = ["Invite"])
    async def invite(self, ctx):
        invite_link = "https://discord.com/api/oauth2/authorize?client_id=945301514946244629&permissions=93248&scope=bot"
        inviteEmbed = discord.Embed(title = "Invite bot!",
								description = f"Click [here]({invite_link}) to invite the bot",
								color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
        await ctx.send(embed = inviteEmbed)

def setup(client):
    client.add_cog(invite(client))